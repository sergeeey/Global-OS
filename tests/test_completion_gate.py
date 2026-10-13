"""Acceptance + adversarial tests for Goal Completion Gate."""

from __future__ import annotations

from global_os.verification.completion_gate import (
    CompletionStatus,
    evaluate_goal_completion,
)


def _goal() -> dict:
    return {
        "goal_id": "g_demo",
        "success_criteria": [
            {"id": "sc_note", "description": "note exists"},
            {"id": "sc_valid", "description": "note valid"},
        ],
        "invariants": ["no_secret_leak"],
    }


def test_achieved_when_all_criteria_reconciled() -> None:
    receipts = [
        {
            "binds_criteria": ["sc_note"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "intended_effect": "write_note",
            "observed_effect": "write_note",
            "tool_response": {"success": True},
        },
        {
            "binds_criteria": ["sc_valid"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "intended_effect": "validate",
            "observed_effect": "validate",
            "tool_response": {"success": True},
        },
    ]
    d = evaluate_goal_completion(goal=_goal(), effect_receipts=receipts)
    assert d.status == CompletionStatus.ACHIEVED
    assert d.llm_used_as_oracle is False
    assert set(d.criteria_met) == {"sc_note", "sc_valid"}


def test_tool_success_alone_is_unknown_not_achieved() -> None:
    receipts = [
        {
            "binds_criteria": ["sc_note", "sc_valid"],
            "reconciliation_status": "EXECUTED",
            "tool_response": {"success": True},
            # world_success absent → GOS-I13
        }
    ]
    d = evaluate_goal_completion(goal=_goal(), effect_receipts=receipts)
    assert d.status == CompletionStatus.UNKNOWN
    assert d.criteria_unknown


def test_llm_claim_ignored() -> None:
    d = evaluate_goal_completion(
        goal=_goal(),
        effect_receipts=[],
        llm_completion_claim="ACHIEVED",
    )
    assert d.status == CompletionStatus.UNKNOWN
    assert d.llm_used_as_oracle is False


def test_invariant_break_forces_failed() -> None:
    d = evaluate_goal_completion(
        goal=_goal(),
        criterion_checks={"sc_note": True, "sc_valid": True},
        invariant_break_flags=["no_secret_leak"],
    )
    assert d.status == CompletionStatus.FAILED


def test_authority_expanded_forces_failed() -> None:
    d = evaluate_goal_completion(
        goal=_goal(),
        criterion_checks={"sc_note": True, "sc_valid": True},
        authority_expanded=True,
    )
    assert d.status == CompletionStatus.FAILED
    assert d.authority_ok is False


def test_partial_when_one_unmet() -> None:
    d = evaluate_goal_completion(
        goal=_goal(),
        criterion_checks={"sc_note": True, "sc_valid": False},
    )
    assert d.status == CompletionStatus.PARTIAL
