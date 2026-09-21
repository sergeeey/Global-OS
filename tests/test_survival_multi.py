from __future__ import annotations

from global_os.evals.survival import (
    DEFAULT_SCENARIOS,
    Injection,
    ScenarioFidelity,
    SurvivalReport,
    SurvivalScenario,
    run_survival_suite,
)


def test_multi_injection_survival_suite_honest_metric():
    report = run_survival_suite()
    assert len(report.runtime_scenarios) == 5
    assert len(report.stub_scenarios) == 0
    assert report.goal_integrity_survival == 1.0
    assert all(s.passed is True for s in report.runtime_scenarios)
    names = {s.name for s in report.runtime_scenarios}
    assert names == {"mid_task_kill", "false_success", "stale_source", "dup_effect", "budget_cut"}
    # Stubs must not inflate the integrity metric even if marked passed by mistake
    polluted = SurvivalReport(
        scenarios=list(report.scenarios)
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


def test_default_scenarios_all_have_runtime_runners():
    assert all(s.fidelity == ScenarioFidelity.RUNTIME_INJECTED for s in DEFAULT_SCENARIOS)
    # Enum still lists injections not yet in DEFAULT — honesty boundary
    covered = {inj for s in DEFAULT_SCENARIOS for inj in s.injections}
    assert Injection.MODEL_SWAP not in covered
    assert Injection.API_OUTAGE not in covered
