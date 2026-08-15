"""Auth service entrypoint — serves auth requests from the `queue:auth` Redis queue."""

import service as auth
from common.rpc import RPCWorker

worker = RPCWorker("auth")

worker.register("signup_user")(auth.signup_user)
worker.register("login_user")(auth.login_user)
worker.register("signup_employer")(auth.signup_employer)
worker.register("login_employer")(auth.login_employer)
worker.register("get_account_from_token")(auth.get_account_from_token)

if __name__ == "__main__":
    worker.run()
