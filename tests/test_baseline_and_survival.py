from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.evals.organization import (
    compare_all_topologies,
    compare_baselines,
    evaluate_kill_criteria,
    summarize_h_org_001,
)
from global_os.evals.survival import Injection, ScenarioFidelity, SurvivalReport, SurvivalScenario
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow


def test_single_agent_vs_organization_baseline(sample_goal):
    goal = sample_goal()
    results = compare_baselines(goal)
    assert results["single_solver"].org_units == 1
    assert results["manager_workers"].org_units > 1
    assert results["single_solver"].success and results["manager_workers"].success


def test_h_org_001_all_topologies_and_kill_criteria(sample_goal):
    goal = sample_goal(goal_id="goal_h_org")
    results = compare_all_topologies(goal)
    assert set(results) == {
        "single_solver",
        "flat_swarm",
        "manager_workers",
        "recursive_hierarchy",
        "hierarchy_verification",
        "dynamically_compiled",
    }
    kill = evaluate_kill_criteria(results)
    assert kill["recursive_default_allowed"] is False
    assert "burns_gains_on_management_cost" in kill["kill_failures"]
    report = summarize_h_org_001(goal)
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert report["fidelity"] == "synthetic_deterministic"
    assert report["kill_criteria"]["preferred_topology"] in results


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
