from __future__ import annotations

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.evals.survival import (
    DEFAULT_SCENARIOS,
    Injection,
    ScenarioFidelity,
    SurvivalReport,
    SurvivalScenario,
)
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow


def test_multi_injection_survival_suite_honest_metric():
    conn = connect_sqlite(":memory:")
    scenarios: list[SurvivalScenario] = []
    for base in DEFAULT_SCENARIOS:
        run_id = f"surv_{base.name}"
        runner = DurableRunner(conn)
        wf = goal_execution_workflow()
        if base.fidelity == ScenarioFidelity.RUNTIME_INJECTED:
            assert Injection.PROCESS_KILL in base.injections
            with pytest.raises(WorkflowAborted):
                runner.start_or_resume(run_id, wf, {}, kill_after_step="plan")
            final = DurableRunner(conn).start_or_resume(run_id, wf, {})
            passed = final.get("phase") == "reported"
            scenarios.append(
                SurvivalScenario(
                    base.name,
                    list(base.injections),
                    ScenarioFidelity.RUNTIME_INJECTED,
                    passed=passed,
                    notes=base.notes,
                )
            )
        else:
            # Stub scenarios are catalogued, not counted as runtime proof.
            scenarios.append(
                SurvivalScenario(
                    base.name,
                    list(base.injections),
                    ScenarioFidelity.STUB,
                    passed=None,
                    notes=f"stub; {base.notes}",
                )
            )

    report = SurvivalReport(scenarios=scenarios)
    assert len(report.runtime_scenarios) == 1
    assert len(report.stub_scenarios) == 4
    assert report.goal_integrity_survival == 1.0
    assert report.stub_completion_rate == 0.0
    # Stubs must not inflate the integrity metric even if marked passed by mistake
    polluted = SurvivalReport(
        scenarios=scenarios
        + [
            SurvivalScenario(
                "fake",
                [Injection.API_OUTAGE],
                ScenarioFidelity.STUB,
                passed=True,
                notes="must not count",
            )
        ]
    )
    assert polluted.goal_integrity_survival == 1.0
    assert polluted.stub_completion_rate == 1.0
