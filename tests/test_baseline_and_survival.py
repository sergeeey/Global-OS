from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.evals.organization import compare_baselines
from global_os.evals.survival import Injection, ScenarioFidelity, SurvivalReport, SurvivalScenario
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow


def test_single_agent_vs_organization_baseline(sample_goal):
    goal = sample_goal()
    results = compare_baselines(goal)
    assert results["single_solver"].org_units == 1
    assert results["manager_workers"].org_units > 1
    assert results["single_solver"].success and results["manager_workers"].success


def test_survival_process_kill_scenario_passes():
    conn = connect_sqlite(":memory:")
    runner = DurableRunner(conn)
    wf = goal_execution_workflow()
    run_id = "survival_kill"
    with pytest.raises(WorkflowAborted):
        runner.start_or_resume(run_id, wf, {}, kill_after_step="execute_tasks")
    final = DurableRunner(conn).start_or_resume(run_id, wf, {})
    scenario = SurvivalScenario(
        "mid_task_kill",
        [Injection.PROCESS_KILL],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=final.get("phase") == "reported",
    )
    report = SurvivalReport(scenarios=[scenario])
    assert report.goal_integrity_survival == 1.0
