from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.evals.survival import DEFAULT_SCENARIOS, Injection, SurvivalReport, SurvivalScenario
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow


def test_multi_injection_survival_suite():
    conn = connect_sqlite(":memory:")
    scenarios: list[SurvivalScenario] = []
    for base in DEFAULT_SCENARIOS:
        run_id = f"surv_{base.name}"
        runner = DurableRunner(conn)
        wf = goal_execution_workflow()
        if Injection.PROCESS_KILL in base.injections:
            with pytest.raises(WorkflowAborted):
                runner.start_or_resume(run_id, wf, {}, kill_after_step="plan")
            final = DurableRunner(conn).start_or_resume(run_id, wf, {})
            passed = final.get("phase") == "reported"
        else:
            # Non-kill injections: ensure workflow still completes (stub resilience)
            final = runner.start_or_resume(run_id, wf, {"injection": base.name})
            passed = final.get("phase") == "reported"
        scenarios.append(
            SurvivalScenario(base.name, list(base.injections), passed=passed, notes="harness")
        )
    report = SurvivalReport(scenarios=scenarios)
    assert report.goal_integrity_survival == 1.0
    assert len(scenarios) == len(DEFAULT_SCENARIOS)
