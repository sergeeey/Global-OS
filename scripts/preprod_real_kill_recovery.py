#!/usr/bin/env python3
"""Real OS process kill/restart recovery probe for PREPROD_SUPERVISED.

Spawns a child process that starts a mission and pauses after brief_select,
then SIGKILLs the child and resumes from a new process.
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


CHILD = r"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, {src!r})
from global_os.runtime.preprod.supervised_mission import start_mission as start_raw

gos = Path(sys.argv[1])
goal = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
target = Path(sys.argv[3])
# Kill after brief_select so gateway_observe is not completed.
# Marker file lets parent know we entered the workflow.
marker = gos / "child_started.json"
marker.write_text(json.dumps({{"pid": __import__("os").getpid()}}), encoding="utf-8")
try:
    out = start_raw(
        goal,
        target_path=target,
        gos_root=gos,
        budget_usd=3.0,
        kill_after_step="brief_select",
        hooks={{"force_model_mode": "reactive"}},
    )
    (gos / "child_result.json").write_text(json.dumps(out), encoding="utf-8")
except Exception as exc:  # noqa: BLE001 — child probe
    (gos / "child_error.json").write_text(repr(exc), encoding="utf-8")
    raise
# Hold briefly so parent can SIGKILL even if kill_after returned.
time.sleep(30)
""".format(src=SRC)


def main() -> int:
    out_dir = ROOT / "artifacts/preprod/final_acceptance/recovery"
    out_dir.mkdir(parents=True, exist_ok=True)
    gos = out_dir / ".gos_kill"
    if gos.exists():
        import shutil

        shutil.rmtree(gos)
    gos.mkdir(parents=True)
    goal_path = ROOT / "examples/goal_repo_audit.json"
    target = ROOT
    child_py = out_dir / "_child_kill_probe.py"
    child_py.write_text(CHILD, encoding="utf-8")

    proc = subprocess.Popen(
        [sys.executable, str(child_py), str(gos), str(goal_path), str(target)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
    )
    # Wait until child marks start or exits.
    deadline = time.time() + 60
    marker = gos / "child_started.json"
    while time.time() < deadline and proc.poll() is None and not marker.exists():
        time.sleep(0.05)
    if not marker.exists() and proc.poll() is not None:
        stdout, stderr = proc.communicate()
        report = {
            "ok": False,
            "reason": "child_exited_before_marker",
            "returncode": proc.returncode,
            "stdout": stdout.decode("utf-8", errors="replace")[-2000:],
            "stderr": stderr.decode("utf-8", errors="replace")[-2000:],
        }
        (out_dir / "REAL_KILL_RECOVERY.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 1

    # Hard kill the OS process (not an in-process exception simulation).
    os.kill(proc.pid, signal.SIGKILL)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass

    # Resume in a fresh process.
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    resume = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json,sys; from pathlib import Path; "
                "from global_os.runtime.preprod import resume_mission, status_mission; "
                f"gos=Path({str(gos)!r}); "
                "st=status_mission(gos_root=gos); "
                "rid=st['run_id']; "
                "out=resume_mission(gos_root=gos, run_id=rid); "
                "print(json.dumps({'status_before': st, 'delivery': out}, default=str))"
            ),
        ],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    report = {
        "ok": resume.returncode == 0,
        "child_pid": proc.pid,
        "child_returncode": proc.returncode,
        "signal": "SIGKILL",
        "resume_returncode": resume.returncode,
        "resume_stdout": resume.stdout[-4000:],
        "resume_stderr": resume.stderr[-4000:],
    }
    if resume.returncode == 0:
        try:
            payload = json.loads(resume.stdout)
            delivery = payload.get("delivery") or {}
            report["terminal_status"] = delivery.get("terminal_status")
            report["run_id"] = delivery.get("run_id")
            report["tool_calls"] = delivery.get("tool_calls")
            # Audit Goal should SUCCEED after resume without silent tool replay.
            report["ok"] = delivery.get("terminal_status") == "SUCCEEDED"
            calls = delivery.get("tool_calls") or {}
            report["no_silent_replay"] = int(calls.get("repo.audit") or 0) <= 1
            report["ok"] = bool(report["ok"] and report["no_silent_replay"])
        except json.JSONDecodeError:
            report["ok"] = False
            report["parse_error"] = True

    (out_dir / "REAL_KILL_RECOVERY.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
