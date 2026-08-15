"""
Subprocess wrapper around helm/kubectl for provisioning a session's mock
topology and running its verifier Job. Every call here is mocked out in
tests (tests/test_k8s_runner.py) — nothing runs against a real cluster
unless SANDBOX_KUBE_CONTEXT points at one that's actually reachable.

See docs/Sandbox_Architecture.md section 3 for where this sits in the
overall session lifecycle.
"""

import json
import os
import subprocess
import time

CHART_ROOT = os.getenv(
    "SANDBOX_CHART_ROOT",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "charts"),
)
KUBE_CONTEXT = os.getenv("SANDBOX_KUBE_CONTEXT", "kind-talentbridge-sandbox")
KUBECONFIG_PATH = os.getenv("SANDBOX_KUBECONFIG", os.path.expanduser("~/.kube/config"))
POLL_INTERVAL_SECONDS = 2


class K8sError(RuntimeError):
    pass


def _kubectl(*args):
    return ["kubectl", "--kubeconfig", KUBECONFIG_PATH, "--context", KUBE_CONTEXT, *args]


def _helm(*args):
    return ["helm", "--kubeconfig", KUBECONFIG_PATH, "--kube-context", KUBE_CONTEXT, *args]


def _run(args, input_text=None):
    result = subprocess.run(args, input=input_text, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise K8sError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def install_topology(session_id: str, namespace: str, helm_chart: str, components: list) -> None:
    chart_path = os.path.join(CHART_ROOT, os.path.basename(helm_chart))
    _run(_helm(
        "upgrade", "--install", session_id, chart_path,
        "--namespace", namespace, "--create-namespace",
        "--set-json", f"components={json.dumps(components)}",
        "--wait", "--timeout", "180s",
    ))


def destroy_topology(session_id: str, namespace: str) -> None:
    subprocess.run(_helm("uninstall", session_id, "--namespace", namespace),
                    capture_output=True, text=True, check=False)
    subprocess.run(_kubectl("delete", "namespace", namespace, "--ignore-not-found", "--wait=false"),
                    capture_output=True, text=True, check=False)


def run_verifier(session_id: str, namespace: str, image: str, command: list, timeout_seconds: int) -> dict:
    job_name = f"verify-{session_id}"
    _delete_job_if_exists(job_name, namespace)
    _run(_kubectl("apply", "-f", "-"), input_text=_verifier_job_manifest(job_name, namespace, image, command))

    deadline = time.time() + timeout_seconds
    status = "running"
    while time.time() < deadline:
        status = _job_status(job_name, namespace)
        if status in ("succeeded", "failed"):
            break
        time.sleep(POLL_INTERVAL_SECONDS)
    else:
        status = "timed_out"

    return {"passed": status == "succeeded", "status": status, "logs": _job_logs(job_name, namespace)}


def _job_status(job_name: str, namespace: str) -> str:
    succeeded = _run(_kubectl("get", "job", job_name, "-n", namespace, "-o", "jsonpath={.status.succeeded}")).strip()
    if succeeded == "1":
        return "succeeded"
    failed = _run(_kubectl("get", "job", job_name, "-n", namespace, "-o", "jsonpath={.status.failed}")).strip()
    if failed and int(failed) > 0:
        return "failed"
    return "running"


def _job_logs(job_name: str, namespace: str) -> str:
    try:
        return _run(_kubectl("logs", f"job/{job_name}", "-n", namespace))
    except K8sError as e:
        return str(e)


def _delete_job_if_exists(job_name: str, namespace: str) -> None:
    subprocess.run(_kubectl("delete", "job", job_name, "-n", namespace, "--ignore-not-found", "--wait=false"),
                    capture_output=True, text=True, check=False)


def _verifier_job_manifest(job_name: str, namespace: str, image: str, command: list) -> str:
    command_lines = "\n".join(f"            - {_yaml_quote(arg)}" for arg in command)
    return f"""apiVersion: batch/v1
kind: Job
metadata:
  name: {job_name}
  namespace: {namespace}
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: verifier
          image: {image}
          command:
{command_lines}
"""


def _yaml_quote(value) -> str:
    return '"' + str(value).replace('"', '\\"') + '"'
