from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.runtime.workflows import (
    DurableRunner,
    WorkflowAborted,
    WorkflowDefinition,
    WorkflowStep,
    goal_execution_workflow,
)


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


def test_succeeded_rerun_does_not_reexecute_last_step():
    """Regression: final SUCCEEDED must not erase last-step COMPLETED for resume."""
    conn = connect_sqlite(":memory:")
    runner = DurableRunner(conn)
    calls = {"n": 0}

    def step_a(state: dict) -> dict:
        out = dict(state)
        out["a"] = 1
        return out

    def step_b(state: dict) -> dict:
        calls["n"] += 1
        out = dict(state)
        out["b"] = calls["n"]
        return out

    wf = WorkflowDefinition(
        name="idempotency_probe",
        steps=[WorkflowStep("a", step_a), WorkflowStep("b", step_b)],
    )
    first = runner.start_or_resume("run_succ_001", wf, {})
    assert first["b"] == 1
    assert calls["n"] == 1

    second = runner.start_or_resume("run_succ_001", wf, {})
    assert second["b"] == 1
    assert calls["n"] == 1, "last step must not re-run after SUCCEEDED"
