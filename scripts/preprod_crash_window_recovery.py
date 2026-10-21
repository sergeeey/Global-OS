#!/usr/bin/env python3
"""Crash after sandbox write effect, before DurableRunner checkpoint.

Measures actual tool executions before/after resume, successful effect receipts,
and idempotency cache hits.  A repeated write is a failure even if the bytes and
mtime are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import sysconfig
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
# A venv python.exe can be a trampoline that spawns the real interpreter
# (Popen.pid != os.getpid()).  Use the base interpreter and add the venv
# site-packages explicitly so the probe kills the process it can identify.
PYTHON = str(getattr(sys, "_base_executable", sys.executable))
_PATHS = sysconfig.get_paths()
SITE = [p for p in (_PATHS.get("purelib"), _PATHS.get("platlib")) if p]
CHILD_ENV = dict(os.environ)
CHILD_ENV["PYTHONPATH"] = os.pathsep.join([SRC, *SITE, CHILD_ENV.get("PYTHONPATH", "")])

CHILD = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, {src!r})
from global_os.runtime.preprod.supervised_mission import start_mission as start_raw

gos = Path(sys.argv[1])
goal = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
target = Path(sys.argv[3])
(gos / "child_started.json").write_text(
    json.dumps({{"pid": __import__("os").getpid()}}), encoding="utf-8"
)
# Crash inside gateway_observe AFTER workspace.write_text effect, before step checkpoint.
start_raw(
    goal,
    target_path=target,
    gos_root=gos,
    budget_usd=5.0,
    hooks={{
        "force_model_mode": "reactive",
        "max_model_cycles": 8,
        "crash_after_tool": "workspace.write_text",
        "crash_after_tool_wait_for_parent": True,
    }},
)
'''.format(src=SRC)

RESUME = r'''
import json, sys
from pathlib import Path
from global_os.kernel.authority.durable_gate import SqliteDurableGateStore
from global_os.runtime.preprod import resume_mission, status_mission

hits = []
claims = []
_get = SqliteDurableGateStore.get_idempotent_receipt
_claim = SqliteDurableGateStore.claim_idempotency

def get(self, key):
    receipt = _get(self, key)
    if receipt is not None:
        hits.append(key)
    return receipt

def claim(self, key):
    ok = _claim(self, key)
    claims.append({"key": key, "claimed": bool(ok)})
    return ok

SqliteDurableGateStore.get_idempotent_receipt = get
SqliteDurableGateStore.claim_idempotency = claim

gos = Path(sys.argv[1])
st = status_mission(gos_root=gos)
out = resume_mission(gos_root=gos, run_id=st["run_id"])
print(json.dumps({
    "status_before": st,
    "delivery": out,
    "idempotency_cache_hits": hits,
    "idempotency_claim_attempts": claims,
}, default=str))
'''


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _observe(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "sha256": None, "size": None, "mtime_ns": None,
                "ctime_ns": None, "inode": None}
    data = path.read_bytes()
    st = path.stat()
    return {
        "exists": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "mtime_ns": st.st_mtime_ns,
        "ctime_ns": st.st_ctime_ns,
        "inode": getattr(st, "st_ino", None),
    }


def _checkpoints(db: Path) -> list[dict]:
    if not db.exists():
        return []
    with sqlite3.connect(db) as conn:
        return [
            {"step_index": r[0], "step_name": r[1], "status": r[2]}
            for r in conn.execute(
                "select step_index, step_name, status from workflow_checkpoints "
                "order by step_index"
            )
        ]


def _counts(calls: dict) -> dict:
    return {"workspace.write_text": int(calls.get("workspace.write_text", 0))}


def main() -> int:
    out = ROOT / "artifacts/preprod/final_acceptance/recovery"
    out.mkdir(parents=True, exist_ok=True)
    gos = out / ".gos_crash_window"
    sandbox = out / "crash_window_sandbox"
    if gos.exists():
        shutil.rmtree(gos)
    if sandbox.exists():
        shutil.rmtree(sandbox)
    gos.mkdir(parents=True)
    sandbox.mkdir(parents=True)
    (sandbox / "README.md").write_text("# crash window\n", encoding="utf-8")
    (sandbox / "app.py").write_text("VALUE = 1\n", encoding="utf-8")

    goal = {
        "schema_version": "0.1.0",
        "goal_id": "goal_crash_window_001",
        "version": 1,
        "tenant_id": "tenant_local",
        "workspace_id": "ws_se",
        "objective": {"text": "Inventory, read README, write FIX_APPLIED.txt, audit."},
        "success_criteria": [
            {"id": "sc_inv", "description": "workspace inventory with file listing"},
            {"id": "sc_read", "description": "read workspace file README"},
            {"id": "sc_write", "description": "apply fix by write file FIX_APPLIED.txt in workspace"},
            {"id": "sc_audit", "description": "verified engineering report with evidence"},
        ],
        "invariants": ["sandbox_target_only"],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 3,
            "capabilities": ["filesystem.read", "filesystem.write", "git.read"],
        },
        "evidence_requirements": {"major_finding": {"verification_tier": 2}},
        "termination": ["success_criteria_met"],
        "created_at": "2026-10-14T00:00:00+00:00",
    }
    goal_path = out / "goal_crash_window.json"
    goal_path.write_text(json.dumps(goal, indent=2), encoding="utf-8")
    child_py = out / "_child_crash_window.py"
    child_py.write_text(CHILD, encoding="utf-8")
    resume_py = out / "_resume_crash_window.py"
    resume_py.write_text(RESUME, encoding="utf-8")

    proc = subprocess.Popen(
        [PYTHON, str(child_py), str(gos), str(goal_path), str(sandbox)],
        cwd=str(ROOT),
        env=CHILD_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    marker = None
    deadline = time.time() + 90
    while time.time() < deadline:
        for cand in gos.glob("missions/*/effect_pre_checkpoint.json"):
            marker = cand
            break
        if marker is not None or proc.poll() is not None:
            break
        time.sleep(0.05)

    if marker is None:
        stdout, stderr = proc.communicate(timeout=5)
        report = {
            "ok": False,
            "reason": "effect_pre_checkpoint_missing",
            "returncode": proc.returncode,
            "stdout": stdout.decode("utf-8", errors="replace")[-2000:],
            "stderr": stderr.decode("utf-8", errors="replace")[-2000:],
        }
        (out / "CRASH_WINDOW_RECOVERY.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 1

    run_dir = marker.parent
    marker_data = _read_json(marker)
    child_started = _read_json(gos / "child_started.json")
    calls_before = _read_json(run_dir / "tool_calls.json")
    effect_before = _observe(sandbox / "FIX_APPLIED.txt")
    checkpoints_before = _checkpoints(run_dir / "workflow.sqlite")
    observe_completed_before = any(
        c["step_name"] == "gateway_observe" and c["status"] == "COMPLETED"
        for c in checkpoints_before
    )
    pid_match = (
        child_started.get("pid") == proc.pid == marker_data.get("pid")
    )

    # Kill the still-running child from the parent (cross-platform).
    was_running = proc.poll() is None
    killed_by_probe = False
    if was_running:
        proc.kill()
        proc.wait(timeout=10)
        killed_by_probe = True

    env = dict(CHILD_ENV)
    env["PYTHONPATH"] = SRC + os.pathsep + os.pathsep.join(SITE) + os.pathsep + env.get("PYTHONPATH", "")
    resume = subprocess.run(
        [PYTHON, str(resume_py), str(gos)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    effect_after = _observe(sandbox / "FIX_APPLIED.txt")
    calls_after = _read_json(run_dir / "tool_calls.json")
    checkpoints_after = _checkpoints(run_dir / "workflow.sqlite")
    before_count = _counts(calls_before)["workspace.write_text"]
    after_count = _counts(calls_after)["workspace.write_text"]
    after_resume = max(0, after_count - before_count)

    payload = {}
    if resume.returncode == 0:
        try:
            payload = json.loads(resume.stdout)
        except json.JSONDecodeError:
            payload = {}
    delivery = payload.get("delivery") or {}
    terminal = delivery.get("terminal_status")
    receipts = list((delivery.get("evidence") or {}).get("effect_receipts") or [])
    write_receipts = [
        r for r in receipts
        if r.get("tool_id") == "workspace.write_text" and r.get("world_success") is True
    ]
    hits = list(payload.get("idempotency_cache_hits") or [])
    claims = list(payload.get("idempotency_claim_attempts") or [])
    write_hits = [h for h in hits if "workspace-write_text" in h]
    write_claims = [c for c in claims if "workspace-write_text" in str(c.get("key", ""))]

    if write_hits:
        prevented = len(write_hits)
    elif after_resume == 0:
        prevented = "UNKNOWN"
    else:
        prevented = 0

    report = {
        "ok": bool(
            effect_before["exists"]
            and effect_after["exists"]
            and effect_before["sha256"] == effect_after["sha256"]
            and before_count == 1
            and after_resume == 0
            and len(write_receipts) == 1
            and terminal == "SUCCEEDED"
            and killed_by_probe
            and proc.returncode is not None
            and proc.returncode != 0
            and pid_match
            and not observe_completed_before
        ),
        "pid_match": pid_match,
        "child_pid": proc.pid,
        "marker_pid": marker_data.get("pid"),
        "started_pid": child_started.get("pid"),
        "was_running_before_kill": was_running,
        "killed_by_probe": killed_by_probe,
        "child_returncode": proc.returncode,
        "tool_executions_before_crash": before_count,
        "tool_executions_after_resume": after_resume,
        "tool_executions_total": after_count,
        "external_effects_total": after_count,
        "write_receipt_count": len(write_receipts),
        "receipt_count": len(receipts),
        "idempotency_replays_prevented": prevented,
        "idempotency_cache_hits": hits,
        "idempotency_claim_attempts": claims,
        "idempotency_write_claim_attempts": write_claims,
        "effect_before": effect_before,
        "effect_after": effect_after,
        "effect_sha_unchanged": effect_before["sha256"] == effect_after["sha256"],
        "mtime_unchanged": effect_before["mtime_ns"] == effect_after["mtime_ns"],
        "checkpoints_before": checkpoints_before,
        "checkpoints_after": checkpoints_after,
        "observe_completed_before_kill": observe_completed_before,
        "terminal_status": terminal,
        "resume_returncode": resume.returncode,
        "resume_stderr": resume.stderr[-2000:],
        "effect_marker": str(marker),
    }
    (out / "CRASH_WINDOW_RECOVERY.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
