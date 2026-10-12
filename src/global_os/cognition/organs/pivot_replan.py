"""Failure-driven replan stub — bounded pivots; no silent Goal overwrite."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.runtime.events.ledger import EventLedger


class PivotError(Exception):
    pass


def pivot_on_failure(
    *,
    goal: dict[str, Any],
    active_plan: dict[str, Any],
    failure: dict[str, Any],
    attempt_budget: int,
    ledger: EventLedger | None = None,
    tenant_id: str = "tenant_local",
    workspace_id: str = "ws_dev",
    prior_failed_approaches: set[str] | None = None,
) -> dict[str, Any]:
    """Decide PIVOT / RETRY_BOUNDED / ESCALATE / STOP with ledger retention."""
    if attempt_budget < 0:
        raise PivotError("attempt_budget must be >= 0")
    why = failure.get("why_failed")
    if not why:
        raise PivotError("INVALID_FAILURE: why_failed required")

    approach = str(failure.get("approach") or failure.get("task_id") or "unknown")
    failed = set(prior_failed_approaches or [])

    if ledger is not None:
        ledger.append(
            event_type="null_result.recorded",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=str(goal.get("goal_id")),
            payload={
                "attempt": failure.get("attempt_id") or new_id("att"),
                "why_failed": why,
                "approach": approach,
            },
            producer="cognition.organs.pivot_replan",
        )

    if attempt_budget == 0:
        return {
            "decision": "STOP",
            "reason": "attempt_budget_exhausted",
            "goal_content_hash": goal.get("content_hash"),
            "remaining_budget": 0,
        }

    if approach in failed and not failure.get("new_evidence"):
        return {
            "decision": "ESCALATE",
            "reason": "repeat_failed_approach_without_new_evidence",
            "goal_content_hash": goal.get("content_hash"),
            "remaining_budget": attempt_budget,
        }

    # Material pivot: change strategy field vs active plan (Q-P6 failure-informed)
    excluded = sorted(failed | {approach})
    new_approach = f"alt_after_{approach}"
    new_plan = deepcopy(active_plan)
    new_plan["plan_id"] = new_id("plan")
    new_plan["supersedes_plan_id"] = active_plan.get("plan_id")
    new_plan["pivot_from_failure"] = why
    new_plan["strategy_variant"] = new_approach
    new_plan["excluded_approaches"] = excluded
    new_plan.pop("content_hash", None)
    new_plan["content_hash"] = content_hash(
        {k: v for k, v in new_plan.items() if k != "content_hash"}
    )

    return {
        "decision": "PIVOT",
        "amended_plan": new_plan,
        "selection": {
            "mechanism": "failure_informed",
            "why_failed": why,
            "excluded_approaches": excluded,
            "new_approach": new_approach,
            "avoids_failure_mode": f"do_not_repeat:{approach}:{why}",
            "serves_criteria": "terminal_success_criteria",
        },
        "handoff_to": "orchestration",
        "remaining_budget": attempt_budget - 1,
        "goal_content_hash": goal.get("content_hash"),
        "goal_version_unchanged": True,
    }
