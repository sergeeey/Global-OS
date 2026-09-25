"""Real OS process death + cold resume from durable SQLite (LH-FC-LOGICAL-PROCESS-KILL).

Controller starts child process A → waits for on-disk checkpoint → kills A →
starts recovery in process B (this process) from the same DB file only.
PIDs must differ; child must be gone before resume.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from global_os.adapters.storage import connect_sqlite
from global_os.runtime.workflows import (
    DurableRunner,
    WorkflowAborted,
    WorkflowDefinition,
    WorkflowStep,
)


def _workflow(goal_id: str, effects_path: Path) -> WorkflowDefinition:
    def step_plan(state: dict[str, Any]) -> dict[str, Any]:
        state = dict(state)
        state["phase"] = "planned"
        state["goal_id"] = goal_id
        state["worker_pid"] = os.getpid()
        return state

    def step_act(state: dict[str, Any]) -> dict[str, Any]:
        state = dict(state)
        # Persist material effect count on disk so cross-process uniqueness is measurable.
        n = 0
        if effects_path.is_file():
            n = int(effects_path.read_text(encoding="utf-8").strip() or "0")
        n += 1
        effects_path.write_text(str(n), encoding="utf-8")
        state["phase"] = "acted"
        state["effects"] = n
        state["act_pid"] = os.getpid()
        return state

    def step_report(state: dict[str, Any]) -> dict[str, Any]:
        state = dict(state)
        state["phase"] = "reported"
        state["report_pid"] = os.getpid()
        return state

    return WorkflowDefinition(
        name="lh48_os_kill_wf",
        steps=[
            WorkflowStep("plan", step_plan),
            WorkflowStep("act", step_act),
            WorkflowStep("report", step_report),
        ],
    )


def child_run(*, db_path: Path, run_id: str, goal_id: str, marker: Path, effects_path: Path) -> None:
    """Run until plan checkpoint, signal ready, then wait to be killed."""
    conn = connect_sqlite(db_path)
    runner = DurableRunner(conn)
    wf = _workflow(goal_id, effects_path)
    try:
        runner.start_or_resume(run_id, wf, {"phase": "init"}, kill_after_step="plan")
    except WorkflowAborted:
        marker.write_text(
            json.dumps({"pid": os.getpid(), "phase": "planned"}),
            encoding="utf-8",
        )
        while True:
            time.sleep(1.0)
    raise RuntimeError("child completed without abort — expected kill_after_step=plan")


def run_os_process_kill_resume(*, goal_id: str, work_dir: Path, timeout_s: float = 30.0) -> dict[str, Any]:
    """Controller: spawn child, kill after checkpoint, resume in this process from disk."""
    work_dir.mkdir(parents=True, exist_ok=True)
    db_path = work_dir / "lh48_durable.sqlite"
    marker = work_dir / "checkpoint_ready.json"
    effects_path = work_dir / "material_effects.txt"
    result_path = work_dir / "os_kill_result.json"
    run_id = "lh48_os_kill_run"

    for p in (marker, effects_path, result_path):
        if p.exists():
            p.unlink()
    if db_path.exists():
        db_path.unlink()

    child_cmd = [
        sys.executable,
        "-m",
        "global_os.evals.survival.os_process_kill",
        "child",
        "--db",
        str(db_path),
        "--run-id",
        run_id,
        "--goal-id",
        goal_id,
        "--marker",
        str(marker),
        "--effects",
        str(effects_path),
    ]
    # Ensure child can import global_os even when parent only mutated sys.path.
    src_root = str(Path(__file__).resolve().parents[3])
    env = os.environ.copy()
    prev = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_root if not prev else src_root + os.pathsep + prev

    child = subprocess.Popen(child_cmd, env=env)
    initial_pid = child.pid
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        if marker.is_file():
            break
        if child.poll() is not None:
            # Capture stderr if any for diagnosis
            raise RuntimeError(f"child exited early code={child.returncode}")
        time.sleep(0.05)
    else:
        child.kill()
        child.wait(timeout=5)
        raise TimeoutError("child did not write checkpoint marker in time")

    marker_payload = json.loads(marker.read_text(encoding="utf-8"))
    # Hard kill — no graceful cleanup (closer to crash)
    child.kill()
    child.wait(timeout=10)
    child_gone = child.poll() is not None

    # Cold resume in a different process identity (this controller process)
    restart_pid = os.getpid()
    conn = connect_sqlite(db_path)
    resumed = DurableRunner(conn).start_or_resume(
        run_id, _workflow(goal_id, effects_path), {"phase": "init"}
    )
    effects = int(effects_path.read_text(encoding="utf-8").strip()) if effects_path.is_file() else 0

    out = {
        "kind": "os_process_kill_cold_resume",
        "passed": (
            child_gone
            and initial_pid != restart_pid
            and resumed.get("phase") == "reported"
            and resumed.get("goal_id") == goal_id
            and effects == 1
            and resumed.get("act_pid") == restart_pid
        ),
        "initial_pid": initial_pid,
        "restart_pid": restart_pid,
        "child_returncode": child.returncode,
        "child_gone": child_gone,
        "marker": marker_payload,
        "final_phase": resumed.get("phase"),
        "goal_id": resumed.get("goal_id"),
        "effects": effects,
        "act_pid": resumed.get("act_pid"),
        "db_path": str(db_path),
    }
    result_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="os_process_kill")
    sub = parser.add_subparsers(dest="cmd", required=True)
    child = sub.add_parser("child")
    child.add_argument("--db", required=True)
    child.add_argument("--run-id", required=True)
    child.add_argument("--goal-id", required=True)
    child.add_argument("--marker", required=True)
    child.add_argument("--effects", required=True)
    ctrl = sub.add_parser("controller")
    ctrl.add_argument("--goal-id", required=True)
    ctrl.add_argument("--work-dir", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "child":
        child_run(
            db_path=Path(args.db),
            run_id=args.run_id,
            goal_id=args.goal_id,
            marker=Path(args.marker),
            effects_path=Path(args.effects),
        )
        return 0
    out = run_os_process_kill_resume(goal_id=args.goal_id, work_dir=Path(args.work_dir))
    print(json.dumps(out))
    return 0 if out["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
