"""Contour A Achiever organ loop + Completion Gate wiring."""

from __future__ import annotations

import pytest

from global_os.cognition.organs import run_achiever_organ_loop
from global_os.common.hashing import content_hash
from global_os.evals.challenge_ga import run_organ_fixture_loop
from global_os.evals.mission_learning import (
    SkillTransferForbidden,
    prepare_skill_transfer_trial,
    run_skill_transfer_trial_gated,
)
from global_os.verification.completion_gate import CompletionStatus


def _demo_goal() -> dict:
    body = {
        "goal_id": "goal_achiever_demo_001",
        "version": 1,
        "objective": {"text": "produce verified note"},
        "success_criteria": [
            {"id": "sc_note", "description": "note exists"},
            {"id": "sc_valid", "description": "note valid"},
        ],
        "invariants": ["no_secret_leak"],
        "forbidden_outcomes": [],
        "authority": {"capabilities": ["filesystem.read"]},
    }
    body["content_hash"] = content_hash(body)
    return body


def test_fixture_loop_exposes_completion_gate_not_achieved_on_naive() -> None:
    out = run_organ_fixture_loop(attempt_budget=2, simulate_failure=True)
    assert out["challenge_win_claimed"] is False
    gate = out["completion_gate"]
    assert gate["status"] in {
        CompletionStatus.FAILED.value,
        CompletionStatus.PARTIAL.value,
    }
    assert "sc_ops" in gate["criteria_unmet"]
    assert any(e.startswith("completion:") for e in out["events"])


def test_achiever_loop_achieves_when_receipts_reconcile() -> None:
    goal = _demo_goal()

    def attempt_fn(g, plan, route):  # type: ignore[no-untyped-def]
        del g, plan, route
        return {
            "effect_receipts": [
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
            ],
            "world_effects": False,
            "challenge_win_claimed": False,
        }

    result = run_achiever_organ_loop(goal, attempt_fn=attempt_fn, attempt_budget=2)
    assert result.stop == "STOP_SUCCESS"
    assert result.completion.status == CompletionStatus.ACHIEVED
    assert result.challenge_win_claimed is False
    assert result.world_effects is False


def test_achiever_loop_pivots_then_stops_without_false_win() -> None:
    goal = _demo_goal()
    calls = {"n": 0}

    def attempt_fn(g, plan, route):  # type: ignore[no-untyped-def]
        del g, plan, route
        calls["n"] += 1
        return {
            "effect_receipts": [],
            "criterion_checks": {"sc_note": False, "sc_valid": False},
            "failure": {
                "attempt_id": f"a{calls['n']}",
                "approach": f"approach_{calls['n']}",
                "why_failed": "criteria_unmet",
            },
            "world_effects": False,
        }

    result = run_achiever_organ_loop(goal, attempt_fn=attempt_fn, attempt_budget=2)
    assert result.challenge_win_claimed is False
    assert result.completion.status != CompletionStatus.ACHIEVED
    assert result.pivots >= 1
    assert result.stop in {
        "STOP_NO_STRATEGY",
        "STOP_FAILED",
        "STOP_INCONCLUSIVE",
        "STOP_ESCALATION",
    }


def test_skill_transfer_blocked_while_challenge_not_started() -> None:
    prep = prepare_skill_transfer_trial()
    assert prep.transfer_allowed is False
    assert prep.continual_si == "NOT_MEASURED"
    assert prep.challenge_execution_status == "NOT_STARTED"
    with pytest.raises(SkillTransferForbidden):
        run_skill_transfer_trial_gated(
            suite_id="suite_z",
            task_ids=["a", "b", "c", "d", "e"],
            baseline_runner=lambda tid, b: False,
            candidate_runner=lambda tid, b: True,
            budget={"tokens": 10},
        )


def test_skill_transfer_forced_override_still_not_continual_si() -> None:
    res = run_skill_transfer_trial_gated(
        suite_id="suite_z",
        task_ids=["a", "b", "c", "d", "e"],
        baseline_runner=lambda tid, b: False,
        candidate_runner=lambda tid, b: True,
        budget={"tokens": 10},
        force_prep_override=True,
    )
    assert res.promote_allowed is False
    assert "continual_si_not_measured" in res.reason
