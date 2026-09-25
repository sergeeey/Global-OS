"""Real OS process kill + cold resume regression (LH-FC-LOGICAL-PROCESS-KILL)."""

from __future__ import annotations

import os

from global_os.evals.survival.os_process_kill import run_os_process_kill_resume


def test_os_process_kill_cold_resume_distinct_pids(tmp_path):
    out = run_os_process_kill_resume(goal_id="goal_os_kill_test", work_dir=tmp_path / "osk")
    assert out["passed"] is True
    assert out["child_gone"] is True
    assert out["initial_pid"] != out["restart_pid"]
    assert out["restart_pid"] == os.getpid()
    assert out["final_phase"] == "reported"
    assert out["effects"] == 1
    assert out["act_pid"] == out["restart_pid"]
    assert (tmp_path / "osk" / "lh48_durable.sqlite").is_file()
