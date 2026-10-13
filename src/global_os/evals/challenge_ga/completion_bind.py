"""Bind Challenge terminal scorer → Goal Completion Gate (no LLM oracle)."""

from __future__ import annotations

from typing import Any

from global_os.verification.completion_gate import (
    CompletionDecision,
    evaluate_goal_completion,
)


def criterion_checks_from_terminal_score(score: dict[str, Any]) -> dict[str, bool | None]:
    """Map SCORE_RUBRIC fields onto Challenge Goal success_criteria ids."""
    checksum_ok = score.get("checksum") == score.get("sealed_checksum")
    ops_ok = int(score.get("ops") or 0) <= int(score.get("ops_budget_max") or 0)
    api_ok = bool(score.get("property_suite_ok"))
    return {
        "sc_checksum": bool(checksum_ok),
        "sc_ops": bool(ops_ok),
        "sc_api": bool(api_ok),
    }


def receipts_from_terminal_score(score: dict[str, Any]) -> list[dict[str, Any]]:
    """Synthetic EffectReceipts bound to criteria (observation = scorer)."""
    checks = criterion_checks_from_terminal_score(score)
    out: list[dict[str, Any]] = []
    for cid, ok in checks.items():
        out.append(
            {
                "binds_criteria": [cid],
                "reconciliation_status": "RECONCILED" if ok else "DISCREPANCY",
                "world_success": bool(ok),
                "intended_effect": cid,
                "observed_effect": cid if ok else f"failed:{cid}",
                "tool_response": {"success": True},  # tool≠world (GOS-I13)
                "verification_method": "challenge_terminal_scorer",
            }
        )
    return out


def evaluate_challenge_completion(
    goal: dict[str, Any],
    score: dict[str, Any],
    *,
    authority_expanded: bool = False,
    invariant_break_flags: list[str] | None = None,
) -> CompletionDecision:
    """Executable terminal decision for Challenge Goal + sealed scorer."""
    return evaluate_goal_completion(
        goal=goal,
        effect_receipts=receipts_from_terminal_score(score),
        criterion_checks=criterion_checks_from_terminal_score(score),
        invariant_break_flags=invariant_break_flags,
        authority_expanded=authority_expanded,
        llm_completion_claim=None,
    )
