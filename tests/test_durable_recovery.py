from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow


def test_crash_and_resume_completes():
    conn = connect_sqlite(":memory:")
    runner = DurableRunner(conn)
    wf = goal_execution_workflow()
    run_id = "run_kill_001"
    with pytest.raises(WorkflowAborted):
        runner.start_or_resume(
            run_id,
            wf,
            {"goal_id": "goal_x"},
            kill_after_step="organize",
        )
    # New runner instance = process restart
    runner2 = DurableRunner(conn)
    final = runner2.start_or_resume(run_id, wf, {"goal_id": "goal_x"})
    assert final["phase"] == "reported"
    assert "report" in final
    assert final["org"] == "manager_workers"
