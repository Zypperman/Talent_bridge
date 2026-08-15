# Local Development

For first-time setup and the standard Docker Compose workflow, see the top-level
[README](../README.md#setup) — `setup.sh`/`setup.ps1`, then `docker compose up
--build`. This doc covers the things a developer needs once that's running: iterating
on one piece at a time, resetting/seeding data, and poking the system directly.

## Running one service outside Docker

The [README's manual setup section](../README.md#manual-setup-without-docker) covers
running the whole stack as plain processes. The common reason to do this is iterating
on *one* service without rebuilding a container each time:

```bash
# once: local Redis, venv, env vars — see README for the full list
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TALENTBRIDGE_DB_PATH="$(pwd)/data/talentbridge.db"
export REDIS_URL="redis://localhost:6379/0"
export PYTHONPATH="$(pwd)"
```

Then run just the piece you're changing (e.g. teaching-service) locally while leaving
everything else in Docker — as long as `REDIS_URL` and `TALENTBRIDGE_DB_PATH` point at
the *same* Redis and SQLite file the Docker Compose stack is using:

```bash
python services/teaching_service/worker.py
```

Since prompt/logic changes in `service.py` take effect on the next request with no
build step, this is much faster than `docker compose up --build teaching-service` for
prompt iteration — see [teaching-and-evaluation.md](teaching-and-evaluation.md).

Each service's `requirements.txt` under `services/*/` and `gateway/` is what actually
ships in its container; the root [requirements.txt](../requirements.txt) is a
convenience superset for exactly this kind of local, no-Docker iteration.

## Resetting the database

The DB is one file: `data/talentbridge.db`. To start clean:

```bash
docker compose down
rm data/talentbridge.db   # or just delete the file if not using Docker
docker compose up --build   # gateway re-applies schema.sql on startup
```

`schema.sql` is safe to re-run against an existing file (everything is
`CREATE ... IF NOT EXISTS`) — you only need to delete the file if you actually want to
lose data, e.g. wiping test accounts/conversations. There's no seed/fixture data beyond
what [generate_courses.py](../generate_courses.py) creates.

## Seeding / regenerating course content

```bash
docker compose run --rm teaching-service python generate_courses.py
```

This is **not idempotent** — [generate_courses.py](../generate_courses.py) always
`INSERT`s its three hardcoded courses (`COURSES` list at the top of the file) and
AI-generates fresh sections for each via Claude. Running it twice against the same DB
gives you duplicate courses with different generated content each time (the AI drafts
different section text on each run since it's not a deterministic template). If you
want to add/edit a course, edit the `COURSES` list or the generated `sections` content
directly in SQLite — there's no update-in-place path in the script itself.

Requires `OPENROUTER_KEY` to be set (same as teaching-service).

## Creating an admin account

No public signup — see [auth-and-accounts.md](auth-and-accounts.md#why-admin-signup-is-out-of-band).

```bash
docker compose run --rm auth-service python create_admin.py you@example.com yourpassword "Your Name"
```

## Talking to a service's RPC queue directly

Useful for debugging the RPC layer itself, independent of the gateway. From a Python
shell with `REDIS_URL`/`PYTHONPATH` set as above:

```python
import asyncio
from common.rpc import RPCClient

async def main():
    client = RPCClient("auth")
    result = await client.call("login_admin", {"email": "you@example.com", "password": "yourpassword"})
    print(result)

asyncio.run(main())
```

If this hangs until `ServiceUnavailableError`, the worker for that queue isn't running
or isn't reachable at `REDIS_URL` — check `docker compose ps` / `docker compose logs
auth-service` before assuming the request payload is wrong.

## Editing the frontend

`static/index.html` and `static/admin.html` are plain files served straight off disk
by the gateway (no build/watch step) — edit and reload the browser. If the gateway is
running via `docker compose up`, the `static/` directory is baked into the gateway
image at build time (see [gateway/Dockerfile](../gateway/Dockerfile):
`COPY static gateway/static`), so **changes require a gateway rebuild**
(`docker compose up --build gateway`) to show up — unlike running the gateway locally
with `uvicorn --reload`, where edits to `static/*.html` take effect on refresh with no
restart needed at all, since `StaticFiles` reads from disk on every request. See
[frontend.md](frontend.md) for how the pages themselves are structured.

## Tests

There is currently no automated test suite in this repo (no `test_*.py` files) —
verification is manual: run the stack, exercise the flows in a browser. If you add
tests, `pytest` is already the implied convention (a stale `.pytest_cache/` exists
from prior local runs) but nothing is wired into CI or `docker-compose.yml` today.

## Logs

`docker compose logs -f <service>` (`gateway`, `auth-service`, `teaching-service`, or
`redis`). Both `RPCWorker.run()` implementations print a one-line "listening..."
message on startup and nothing else by default — application-level errors surface as
the `{"ok": false, "error": ...}` envelope sent back over RPC (visible in the
*gateway's* response to the browser), not necessarily as service-side log lines, so
when debugging a `ServiceError`, the message returned to the client is often more
informative than the service's own stdout.
