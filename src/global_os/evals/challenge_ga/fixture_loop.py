"""Organ control-flow against Challenge-GA Goal — no world WIN claim.

ADR-0009: eval/T2 harness only. Does not bypass Authority or mutate fixture
to claim Challenge success. Used to deepen Decomposer→Orchestration→Pivot
wiring before human-authorized exec.
"""

from __future__ import annotations

from typing import Any

from global_os.cognition.organs import (
    decompose_goal,
    pivot_on_failure,
    route_task,
)
from global_os.common.hashing import content_hash
from global_os.evals.challenge_ga.completion_bind import evaluate_challenge_completion
from global_os.evals.challenge_ga.scorer import score_terminal_fixture
from global_os.runtime.events import EventLedger


def build_challenge_goal() -> dict[str, Any]:
    """Goal Contract for sealed fixture (terminal criteria only)."""
    body = {
        "goal_id": "goal_challenge_ga_fixture_001",
        "version": 1,
        "objective": {
            "text": (
                "Optimize process_items so sealed checksum is preserved and "
                "ops ≤ 80000 without changing the public signature"
            )
        },
        "success_criteria": [
            {
                "id": "sc_checksum",
                "description": "process_items(list(range(400))) == 7674672",
            },
            {
                "id": "sc_ops",
                "description": "last_ops() <= 80000 after sealed call",
            },
            {
                "id": "sc_api",
                "description": "process_items(list[int]) -> int signature frozen",
            },
        ],
        "invariants": ["no_signature_break", "no_false_ops_instrumentation"],
        "non_goals": ["optimize_global_os_product", "reopen_pilot3_attr"],
        "forbidden_outcomes": ["wrong_checksum", "api_break", "budget_overrun"],
        "authority": {
            "capabilities": ["filesystem.read", "code.execute.sandbox"],
        },
    }
    body["content_hash"] = content_hash(body)
    return body


def run_organ_fixture_loop(
    *,
    attempt_budget: int = 3,
    ledger: EventLedger | None = None,
    simulate_failure: bool = True,
) -> dict[str, Any]:
    """Run Decomposer → Orchestration → optional Pivot. Scores fixture but never
    claims Challenge exec WIN (scorer reflects current naive fixture = not WIN).
    """
    ledger = ledger or EventLedger()
    goal = build_challenge_goal()
    plan = decompose_goal(goal)
    events: list[str] = ["decomposed"]

    # Orchestration: purposeful route for optimize task
    task = {"task_id": "t_optimize", "title": "optimize_process_items"}
    routed = route_task(
        goal=goal,
        plan=plan,
        task=task,
        routing_context={
            "risk": "low",
            "cost_remaining": 1.0,
            "tool_ids": ["filesystem.read"],
            "why_this_tool": "inspect_fixture_source",
            "why_this_model": "cheap_fast_for_plan_bound_edit",
            "alternatives_considered": ["code.execute.sandbox"],
        },
    )
    events.append(f"routed:{routed['decision']}")
    assert routed.get("world_success_claimed") is False

    pivot_out: dict[str, Any] | None = None
    stop = "CONTINUE"
    if simulate_failure:
        # Naive fixture fails ops budget — organs must pivot, not invent WIN
        score = score_terminal_fixture()
        if not score["win"]:
            pivot_out = pivot_on_failure(
                goal=goal,
                active_plan=plan,
                failure={
                    "attempt_id": "att_naive",
                    "approach": "naive_o_n2",
                    "why_failed": "ops_above_budget",
                },
                attempt_budget=attempt_budget,
                ledger=ledger,
            )
            events.append(f"pivot:{pivot_out['decision']}")
            if pivot_out["decision"] in {"STOP", "ESCALATE"}:
                stop = (
                    "STOP_NO_STRATEGY"
                    if pivot_out["decision"] == "STOP"
                    else "STOP_ESCALATION"
                )
            else:
                stop = "PIVOTED_AWAITING_EXEC"
    else:
        score = score_terminal_fixture()

    completion = evaluate_challenge_completion(goal, score)
    events.append(f"completion:{completion.status.value}")
    # Completion ACHIEVED ≠ authorized Challenge WIN (exec gate separate).

    return {
        "goal_content_hash": goal["content_hash"],
        "plan_id": plan["plan_id"],
        "task_advances_criteria": plan.get("task_advances_criteria"),
        "route": routed,
        "pivot": pivot_out,
        "terminal_score": score,
        "completion_gate": completion.to_dict(),
        "challenge_win_claimed": False,  # harness must never self-certify WIN
        "stop": stop,
        "events": events,
        "world_effects": False,
    }
