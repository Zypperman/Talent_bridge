"""
Minimal Redis-backed request/reply RPC used between the gateway and the
auth/teaching services. A client LPUSHes a request onto `queue:<service>`;
the service BRPOPs it, runs a handler, and RPUSHes the result onto a
per-call reply key that the client BLPOPs.
"""

import json
import os
import time
import uuid

import redis
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TIMEOUT_SECONDS = 10
REPLY_KEY_TTL_SECONDS = 30


class ServiceError(Exception):
    """The service handled the request but reported a business-logic error."""


class ServiceUnavailableError(Exception):
    """The service did not reply within the timeout."""


class RPCClient:
    """Async client used by the gateway to call a service over its queue."""

    def __init__(self, service_name: str, timeout: float = DEFAULT_TIMEOUT_SECONDS):
        self._queue = f"queue:{service_name}"
        self._service_name = service_name
        self._timeout = timeout
        self._redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    async def call(self, action: str, payload: dict | None = None):
        reply_key = f"reply:{uuid.uuid4().hex}"
        message = json.dumps({"action": action, "payload": payload or {}, "reply_to": reply_key})
        await self._redis.lpush(self._queue, message)

        # A single long BLPOP can have redis-py's own socket-level read timeout
        # race against the command's `timeout` argument and raise a spurious
        # TimeoutError partway through — same underlying quirk as RPCWorker.run.
        # Loop short blocks instead so a spurious timeout just means "keep waiting".
        deadline = time.monotonic() + self._timeout
        popped = None
        while time.monotonic() < deadline:
            block_for = max(1, min(5, int(deadline - time.monotonic())))
            try:
                popped = await self._redis.blpop(reply_key, timeout=block_for)
            except redis.exceptions.TimeoutError:
                continue
            if popped is not None:
                break

        if popped is None:
            raise ServiceUnavailableError(
                f"{self._service_name} service timed out handling '{action}'"
            )

        envelope = json.loads(popped[1])
        if not envelope.get("ok", False):
            raise ServiceError(envelope.get("error", "Unknown service error"))
        return envelope.get("result")


class RPCWorker:
    """Sync worker loop used by a service process to serve requests from its queue."""

    def __init__(self, service_name: str):
        self._queue = f"queue:{service_name}"
        self._redis = redis.from_url(REDIS_URL, decode_responses=True)
        self._handlers = {}

    def register(self, action):
        def decorator(fn):
            self._handlers[action] = fn
            return fn
        return decorator

    def run(self):
        print(f"[{self._queue}] worker listening...", flush=True)
        while True:
            try:
                item = self._redis.brpop(self._queue, timeout=5)
            except redis.exceptions.TimeoutError:
                # redis-py's own socket timeout can fire around a long block even
                # though Redis itself hasn't timed out yet — harmless, just retry.
                continue
            if item is None:
                continue
            self._handle(item[1])

    def _handle(self, raw: str):
        message = json.loads(raw)
        action = message.get("action")
        payload = message.get("payload") or {}
        reply_key = message.get("reply_to")
        handler = self._handlers.get(action)

        if handler is None:
            envelope = {"ok": False, "error": f"Unknown action '{action}'"}
        else:
            try:
                envelope = {"ok": True, "result": handler(**payload)}
            except ValueError as e:
                envelope = {"ok": False, "error": str(e)}
            except Exception as e:
                envelope = {"ok": False, "error": f"Internal error: {e}"}

        self._redis.rpush(reply_key, json.dumps(envelope))
        self._redis.expire(reply_key, REPLY_KEY_TTL_SECONDS)
