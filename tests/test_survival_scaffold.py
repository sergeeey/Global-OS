from __future__ import annotations

from global_os.evals.survival import DEFAULT_SCENARIOS, SurvivalReport, SurvivalScenario


def test_survival_report_metric():
    report = SurvivalReport(
        scenarios=[
            SurvivalScenario("a", [], passed=True),
            SurvivalScenario("b", [], passed=False),
            SurvivalScenario("c", [], passed=True),
        ]
    )
    assert abs(report.goal_integrity_survival - 2 / 3) < 1e-9
    assert len(DEFAULT_SCENARIOS) >= 5
