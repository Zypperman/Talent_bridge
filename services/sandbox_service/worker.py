"""Sandbox service entrypoint — serves sandbox requests from the `queue:sandbox` Redis queue."""

import service as sandbox
from common.rpc import RPCWorker

worker = RPCWorker("sandbox")

worker.register("list_scenarios")(sandbox.list_scenarios)
worker.register("create_session")(sandbox.create_session)
worker.register("get_session")(sandbox.get_session)
worker.register("list_sessions_for_user")(sandbox.list_sessions_for_user)
worker.register("verify_session")(sandbox.verify_session)
worker.register("destroy_session")(sandbox.destroy_session)

if __name__ == "__main__":
    worker.run()
