from __future__ import annotations

from global_os.evals.survival import ScenarioFidelity, SurvivalReport, SurvivalScenario


def test_survival_report_metric_only_runtime():
    report = SurvivalReport(
        scenarios=[
            SurvivalScenario("a", [], ScenarioFidelity.RUNTIME_INJECTED, passed=True),
            SurvivalScenario("b", [], ScenarioFidelity.RUNTIME_INJECTED, passed=False),
            SurvivalScenario("c", [], ScenarioFidelity.STUB, passed=True),
        ]
    )
    assert abs(report.goal_integrity_survival - 0.5) < 1e-9
    assert report.stub_completion_rate == 1.0
