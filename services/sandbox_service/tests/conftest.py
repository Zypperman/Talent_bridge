import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SERVICE_DIR = os.path.dirname(_TESTS_DIR)
_REPO_ROOT = os.path.dirname(os.path.dirname(_SERVICE_DIR))

# service.py and its siblings (k8s_runner, terraform_runner, scenario_registry)
# are plain top-level modules, imported the same way worker.py imports them in
# production (script directory on sys.path, no package). common.rpc needs the
# repo root on sys.path too.
for _path in (_SERVICE_DIR, _REPO_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)
