#!/usr/bin/env python3
"""SIGKILL after sandbox write effect and before DurableRunner checkpoint.

Proves: external write is not silently re-applied on resume, and is not lost.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")

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
    }},
)
'''.format(src=SRC)


def main() -> int:
    out = ROOT / "artifacts/preprod/final_acceptance/recovery"
    out.mkdir(parents=True, exist_ok=True)
    gos = out / ".gos_crash_window"
    sandbox = out / "crash_window_sandbox"
    if gos.exists():
        import shutil

        shutil.rmtree(gos)
    if sandbox.exists():
        import shutil

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
            {
                "id": "sc_write",
                "description": "apply fix by write file FIX_APPLIED.txt in workspace",
            },
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

    proc = subprocess.Popen(
        [sys.executable, str(child_py), str(gos), str(goal_path), str(sandbox)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    marker = None
    deadline = time.time() + 90
    while time.time() < deadline:
        # Find effect_pre_checkpoint under missions/*/
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

    # Ensure child is dead (hook may have SIGKILL'd itself).
    if proc.poll() is None:
        os.kill(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)

    fix_before = (sandbox / "FIX_APPLIED.txt").exists()
    mtime_before = (
        (sandbox / "FIX_APPLIED.txt").stat().st_mtime_ns if fix_before else None
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    resume = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; from pathlib import Path; "
                "from global_os.runtime.preprod import resume_mission, status_mission; "
                f"gos=Path({str(gos)!r}); st=status_mission(gos_root=gos); "
                "out=resume_mission(gos_root=gos, run_id=st['run_id']); "
                "print(json.dumps({'status_before': st, 'delivery': out}, default=str))"
            ),
        ],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    fix_after = (sandbox / "FIX_APPLIED.txt").exists()
    mtime_after = (sandbox / "FIX_APPLIED.txt").stat().st_mtime_ns if fix_after else None
    write_calls = None
    terminal = None
    if resume.returncode == 0:
        try:
            payload = json.loads(resume.stdout)
            delivery = payload.get("delivery") or {}
            terminal = delivery.get("terminal_status")
            write_calls = (delivery.get("tool_calls") or {}).get("workspace.write_text")
        except json.JSONDecodeError:
            pass

    report = {
        "ok": bool(
            fix_before
            and fix_after
            and mtime_before == mtime_after
            and write_calls == 1
            and terminal == "SUCCEEDED"
            and proc.returncode in {-signal.SIGKILL, -9}
        ),
        "child_returncode": proc.returncode,
        "fix_present_before_resume": fix_before,
        "fix_present_after_resume": fix_after,
        "mtime_unchanged": mtime_before == mtime_after,
        "write_calls_after_resume": write_calls,
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
