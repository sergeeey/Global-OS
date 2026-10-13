"""Contour A Achiever organ loop — beyond Challenge fixture-only wiring.

Decomposer → Orchestration → (optional Pivot) → Completion Gate.
No world effects without Gateway; no Challenge exec; no LLM completion oracle.
ADR-0009: T2 cognition surface only.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from global_os.cognition.organs.decomposer import DecomposerError, decompose_goal
from global_os.cognition.organs.orchestration import OrchestrationError, route_task
from global_os.cognition.organs.pivot_replan import PivotError, pivot_on_failure
from global_os.runtime.events import EventLedger
from global_os.verification.completion_gate import (
    CompletionDecision,
    CompletionStatus,
    evaluate_goal_completion,
)

# Callable returns effect receipts + optional failure dict for this attempt
AttemptFn = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class AchieverLoopResult:
    goal_id: str
    plan_id: str
    stop: str
    completion: CompletionDecision
    events: tuple[str, ...]
    pivots: int
    challenge_win_claimed: bool
    world_effects: bool
    route_decisions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "plan_id": self.plan_id,
            "stop": self.stop,
            "completion": self.completion.to_dict(),
            "events": list(self.events),
            "pivots": self.pivots,
            "challenge_win_claimed": self.challenge_win_claimed,
            "world_effects": self.world_effects,
            "route_decisions": list(self.route_decisions),
            "achieved": self.completion.status == CompletionStatus.ACHIEVED,
        }


class AchieverLoopError(Exception):
    pass


def run_achiever_organ_loop(
    goal: dict[str, Any],
    *,
    attempt_fn: AttemptFn,
    attempt_budget: int = 3,
    ledger: EventLedger | None = None,
    routing_context: dict[str, Any] | None = None,
    authority_expanded: bool = False,
) -> AchieverLoopResult:
    """Run Contour A control flow until Completion Gate settles or budget ends.

    ``attempt_fn(goal, plan, route)`` must return:
      - effect_receipts: list[dict]
      - failure: optional dict with why_failed (triggers pivot)
      - criterion_checks: optional dict[str, bool|None]
      - invariant_break_flags: optional list[str]
      - forbidden_outcomes_observed: optional list[str]
    It must NOT execute Challenge arms or claim WIN.
    """
    if attempt_budget < 0:
        raise AchieverLoopError("attempt_budget must be >= 0")
    ledger = ledger or EventLedger()
    try:
        plan = decompose_goal(goal)
    except DecomposerError as exc:
        raise AchieverLoopError(str(exc)) from exc

    events: list[str] = ["decomposed"]
    route_decisions: list[str] = []
    pivots = 0
    remaining = attempt_budget
    failed_approaches: set[str] = set()
    last_completion: CompletionDecision | None = None
    ctx = dict(routing_context or {})
    if "tool_ids" not in ctx:
        ctx["tool_ids"] = ["filesystem.read"]
    if "why_this_tool" not in ctx:
        ctx["why_this_tool"] = "inspect_bound_goal_artifacts"
    if "why_this_model" not in ctx:
        ctx["why_this_model"] = "cheap_fast_for_plan_bound_work"

    while remaining >= 0:
        task = {"task_id": f"t_attempt_{pivots}", "title": "advance_success_criteria"}
        try:
            routed = route_task(
                goal=goal,
                plan=plan,
                task=task,
                routing_context=ctx,
            )
        except OrchestrationError as exc:
            raise AchieverLoopError(str(exc)) from exc
        route_decisions.append(str(routed.get("decision")))
        events.append(f"routed:{routed.get('decision')}")
        if routed.get("world_success_claimed"):
            raise AchieverLoopError("orchestration claimed world success — forbidden")

        attempt = attempt_fn(goal, plan, routed)
        if attempt.get("challenge_win_claimed"):
            raise AchieverLoopError("attempt_fn claimed Challenge WIN — forbidden")
        if attempt.get("world_effects"):
            raise AchieverLoopError(
                "attempt_fn reported world_effects; Achiever loop is control-only "
                "(Gateway path required for material effects)"
            )

        receipts = list(attempt.get("effect_receipts") or [])
        completion = evaluate_goal_completion(
            goal=goal,
            effect_receipts=receipts,
            criterion_checks=attempt.get("criterion_checks"),
            invariant_break_flags=list(attempt.get("invariant_break_flags") or []),
            authority_expanded=authority_expanded
            or bool(attempt.get("authority_expanded")),
            forbidden_outcomes_observed=list(
                attempt.get("forbidden_outcomes_observed") or []
            ),
            llm_completion_claim=attempt.get("llm_completion_claim"),
        )
        last_completion = completion
        events.append(f"completion:{completion.status.value}")

        if completion.status == CompletionStatus.ACHIEVED:
            return AchieverLoopResult(
                goal_id=str(goal.get("goal_id")),
                plan_id=str(plan.get("plan_id")),
                stop="STOP_SUCCESS",
                completion=completion,
                events=tuple(events),
                pivots=pivots,
                challenge_win_claimed=False,
                world_effects=False,
                route_decisions=tuple(route_decisions),
            )

        failure = attempt.get("failure")
        if not failure and completion.status in {
            CompletionStatus.FAILED,
            CompletionStatus.PARTIAL,
            CompletionStatus.UNKNOWN,
        }:
            failure = {
                "attempt_id": f"att_{pivots}",
                "approach": str(plan.get("strategy_variant") or "primary"),
                "why_failed": completion.reason,
            }

        if not failure:
            break

        if remaining == 0:
            events.append("budget_exhausted")
            break

        try:
            pivot_out = pivot_on_failure(
                goal=goal,
                active_plan=plan,
                failure=failure,
                attempt_budget=remaining,
                ledger=ledger,
                prior_failed_approaches=failed_approaches,
            )
        except PivotError as exc:
            raise AchieverLoopError(str(exc)) from exc

        events.append(f"pivot:{pivot_out['decision']}")
        approach = str(failure.get("approach") or "primary")
        failed_approaches.add(approach)

        if pivot_out["decision"] == "STOP":
            return AchieverLoopResult(
                goal_id=str(goal.get("goal_id")),
                plan_id=str(plan.get("plan_id")),
                stop="STOP_NO_STRATEGY",
                completion=completion,
                events=tuple(events),
                pivots=pivots,
                challenge_win_claimed=False,
                world_effects=False,
                route_decisions=tuple(route_decisions),
            )
        if pivot_out["decision"] == "ESCALATE":
            return AchieverLoopResult(
                goal_id=str(goal.get("goal_id")),
                plan_id=str(plan.get("plan_id")),
                stop="STOP_ESCALATION",
                completion=completion,
                events=tuple(events),
                pivots=pivots,
                challenge_win_claimed=False,
                world_effects=False,
                route_decisions=tuple(route_decisions),
            )

        plan = pivot_out.get("amended_plan") or plan
        remaining = int(pivot_out.get("remaining_budget", remaining - 1))
        pivots += 1

    assert last_completion is not None
    stop = (
        "STOP_FAILED"
        if last_completion.status == CompletionStatus.FAILED
        else "STOP_INCONCLUSIVE"
    )
    return AchieverLoopResult(
        goal_id=str(goal.get("goal_id")),
        plan_id=str(plan.get("plan_id")),
        stop=stop,
        completion=last_completion,
        events=tuple(events),
        pivots=pivots,
        challenge_win_claimed=False,
        world_effects=False,
        route_decisions=tuple(route_decisions),
    )
