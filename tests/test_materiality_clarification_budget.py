from __future__ import annotations

from global_os.cognition.clarification import ClarificationEngine
from global_os.cognition.metareasoning import ReasoningBudgetController, assess_materiality
from global_os.runtime.events import EventLedger


def test_materiality_critical_vs_cosmetic():
    chart = assess_materiality(
        impact="low", probability=0.9, irreversibility="none", goal_sensitivity=0.1
    )
    money = assess_materiality(
        impact="critical", probability=0.5, irreversibility="high", goal_sensitivity=1.0
    )
    assert chart.level.value in {"none", "low"}
    assert money.level.value in {"high", "critical"}
    assert money.ask_human is True


def test_reasoning_budget_does_not_change_verification_tier():
    ctrl = ReasoningBudgetController()
    decision = ctrl.decide(
        {
            "default_effort": "medium",
            "min_effort": "low",
            "max_effort": "high",
            "increase_when": ["verification_failed"],
            "decrease_when": ["confidence_high"],
        },
        verification_tier=3,
        signals={"confidence_high"},
    )
    assert decision.effort == "low"
    assert decision.verification_tier_unchanged == 3

    up = ctrl.decide(
        {
            "default_effort": "low",
            "min_effort": "low",
            "max_effort": "high",
            "increase_when": ["verification_failed"],
            "decrease_when": ["confidence_high"],
        },
        verification_tier=3,
        signals={"verification_failed"},
    )
    assert up.effort == "medium"
    assert up.verification_tier_unchanged == 3


def test_clarification_records_assumption():
    engine = ClarificationEngine(EventLedger())
    policy = {
        "materiality_policy": "materiality_based",
        "ask_when": ["irreversible_action"],
        "assume_when": ["formatting_only", "low_impact"],
        "record_assumption": True,
        "max_rounds": 2,
    }
    result = engine.decide(
        policy,
        situation="formatting_only",
        impact="low",
        probability=0.2,
        irreversibility="none",
        goal_sensitivity=0.1,
        goal_id="goal_x",
        tenant_id="t",
        workspace_id="w",
        assumption_statement="Use JSON output format",
    )
    assert result["action"] == "assume"
    assert result["assumption"]["origin"] == "clarification_skipped"
    assert result["assumption"]["status"] == "ACTIVE"


def test_clarification_asks_on_authority_gap():
    engine = ClarificationEngine(EventLedger())
    policy = {
        "materiality_policy": "materiality_based",
        "ask_when": ["authority_gap"],
        "assume_when": ["formatting_only"],
        "record_assumption": True,
    }
    result = engine.decide(
        policy,
        situation="authority_gap",
        impact="high",
        probability=0.8,
        irreversibility="high",
        goal_sensitivity=1.0,
        goal_id="goal_x",
        tenant_id="t",
        workspace_id="w",
        assumption_statement="should not record",
    )
    assert result["action"] == "ask"
