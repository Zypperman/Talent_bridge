"""Teaching service entrypoint — serves teaching requests from the `queue:teaching` Redis queue."""

import service as teaching
from common.rpc import RPCWorker

worker = RPCWorker("teaching")

worker.register("generate_teaching_reply")(teaching.generate_teaching_reply)
worker.register("evaluate_section")(teaching.evaluate_section)

if __name__ == "__main__":
    worker.run()
