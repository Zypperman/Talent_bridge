"""
Talent Bridge Sandbox Service — provisions per-learner incident-simulation
sessions (a mock data-center topology plus an injected fault), runs each
session's verifier suite, and tears sessions down.

See docs/Sandbox_Architecture.md for the design this implements.
"""

import os
import sqlite3
import uuid
from datetime import datetime, timezone

import k8s_runner
import terraform_runner
from scenario_registry import get as get_scenario, load_all as load_scenarios

_DB_PATH = os.getenv("TALENTBRIDGE_DB_PATH", "/opt/talentbridge/data/talentbridge.db")

_SESSION_COLUMNS = [
    "id", "scenario_id", "user_id", "namespace", "status", "access_command",
    "verification_logs", "error_message", "created_at", "verified_at", "destroyed_at",
]


def _get_db():
    return sqlite3.connect(_DB_PATH, check_same_thread=False)


def list_scenarios():
    return [
        {"id": s["id"], "title": s["title"], "description": s["description"]}
        for s in load_scenarios().values()
    ]


def create_session(scenario_id, user_id):
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario '{scenario_id}'")

    session_id = uuid.uuid4().hex
    namespace = f"sandbox-{session_id[:12]}"
    now = datetime.now(timezone.utc).isoformat()

    db = _get_db()
    db.execute(
        """INSERT INTO sandbox_sessions (id, scenario_id, user_id, namespace, status, created_at)
           VALUES (?, ?, ?, ?, 'provisioning', ?)""",
        (session_id, scenario_id, user_id, namespace, now),
    )
    db.commit()

    try:
        topology = scenario["topology"]
        k8s_runner.install_topology(session_id, namespace, topology["helm_chart"], topology["components"])

        fault = scenario["fault"]
        if fault["layer"] == "infra":
            terraform_runner.apply_fault(session_id, namespace, fault.get("variables", {}))

        entrypoint = topology["components"][0]["name"]
        access_command = (
            f"kubectl --context {k8s_runner.KUBE_CONTEXT} -n {namespace} exec -it deploy/{entrypoint} -- /bin/sh"
        )
        db.execute(
            "UPDATE sandbox_sessions SET status = 'ready', access_command = ? WHERE id = ?",
            (access_command, session_id),
        )
        db.commit()
    except (k8s_runner.K8sError, terraform_runner.TerraformError) as e:
        # Best-effort cleanup so a failed provision doesn't leak a half-built topology.
        k8s_runner.destroy_topology(session_id, namespace)
        db.execute(
            "UPDATE sandbox_sessions SET status = 'error', error_message = ? WHERE id = ?",
            (str(e), session_id),
        )
        db.commit()
        raise ValueError(f"Failed to provision session: {e}")

    return get_session(session_id)


def get_session(session_id):
    db = _get_db()
    row = db.execute(
        f"SELECT {', '.join(_SESSION_COLUMNS)} FROM sandbox_sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Unknown session '{session_id}'")
    return dict(zip(_SESSION_COLUMNS, row))


def list_sessions_for_user(user_id):
    db = _get_db()
    rows = db.execute(
        "SELECT id, scenario_id, status, created_at FROM sandbox_sessions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    return [{"id": r[0], "scenario_id": r[1], "status": r[2], "created_at": r[3]} for r in rows]


def verify_session(session_id):
    session = get_session(session_id)
    if session["status"] not in ("ready", "failed", "passed"):
        raise ValueError(f"Session is '{session['status']}', not ready to verify")

    scenario = get_scenario(session["scenario_id"])
    if scenario is None:
        raise ValueError(f"Unknown scenario '{session['scenario_id']}'")

    db = _get_db()
    db.execute("UPDATE sandbox_sessions SET status = 'verifying' WHERE id = ?", (session_id,))
    db.commit()

    verifier = scenario["verifier"]
    result = k8s_runner.run_verifier(
        session_id, session["namespace"], verifier["image"], verifier["command"],
        verifier.get("timeout_seconds", 120),
    )

    status = "passed" if result["passed"] else "failed"
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        "UPDATE sandbox_sessions SET status = ?, verification_logs = ?, verified_at = ? WHERE id = ?",
        (status, result["logs"], now, session_id),
    )
    db.commit()

    return {"session_id": session_id, "passed": result["passed"], "logs": result["logs"]}


def destroy_session(session_id):
    session = get_session(session_id)
    if session["status"] == "destroyed":
        raise ValueError("Session already destroyed")

    scenario = get_scenario(session["scenario_id"])
    if scenario and scenario["fault"]["layer"] == "infra":
        terraform_runner.destroy_fault(session_id)
    k8s_runner.destroy_topology(session_id, session["namespace"])

    now = datetime.now(timezone.utc).isoformat()
    db = _get_db()
    db.execute(
        "UPDATE sandbox_sessions SET status = 'destroyed', destroyed_at = ? WHERE id = ?",
        (now, session_id),
    )
    db.commit()
    return {"session_id": session_id, "status": "destroyed"}
