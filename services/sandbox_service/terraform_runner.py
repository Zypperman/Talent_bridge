"""
Thin subprocess wrapper around the Terraform CLI. Each sandbox session gets
its own Terraform workspace (named after the session ID) within a shared
root module, so state for concurrent sessions never collides.

See terraform/environments/{local,gcp}/ for the root modules this drives,
and docs/Sandbox_Architecture.md section 3.1 for how a scenario's `fault`
block maps onto this.
"""

import os
import subprocess

TERRAFORM_ENV = os.getenv("SANDBOX_TF_ENV", "local")  # "local" or "gcp"
TERRAFORM_ROOT = os.getenv(
    "SANDBOX_TERRAFORM_ROOT",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "terraform", "environments", TERRAFORM_ENV,
    ),
)


class TerraformError(RuntimeError):
    pass


def _env():
    env = os.environ.copy()
    kubeconfig = os.getenv("SANDBOX_KUBECONFIG")
    if kubeconfig:
        env["TF_VAR_kubeconfig_path"] = kubeconfig
    kube_context = os.getenv("SANDBOX_KUBE_CONTEXT")
    if kube_context:
        env["TF_VAR_kube_context"] = kube_context
    return env


def _run(args):
    result = subprocess.run(
        ["terraform", *args], cwd=TERRAFORM_ROOT, env=_env(),
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise TerraformError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def _select_or_create_workspace(session_id: str) -> None:
    existing = _run(["workspace", "list"])
    names = {line.strip("* ").strip() for line in existing.splitlines() if line.strip()}
    if session_id in names:
        _run(["workspace", "select", session_id])
    else:
        _run(["workspace", "new", session_id])


def apply_fault(session_id: str, namespace: str, variables: dict) -> None:
    """Applies the fault module for a session. `variables` comes straight from
    the scenario's fault.variables block (e.g. target, block_port)."""
    _run(["init", "-input=false"])
    _select_or_create_workspace(session_id)
    var_args = [
        f"-var={key}={value}"
        for key, value in {"session_id": session_id, "namespace": namespace, **variables}.items()
    ]
    _run(["apply", "-auto-approve", "-input=false", *var_args])


def destroy_fault(session_id: str) -> None:
    _run(["init", "-input=false"])
    _select_or_create_workspace(session_id)
    _run(["destroy", "-auto-approve", "-input=false"])
    _run(["workspace", "select", "default"])
    _run(["workspace", "delete", session_id])
