"""Tool/model orchestration stub — proposes routes; never bypasses Authority."""

from __future__ import annotations

from typing import Any


class OrchestrationError(Exception):
    pass


def route_task(
    *,
    goal: dict[str, Any],
    plan: dict[str, Any],
    task: dict[str, Any],
    routing_context: dict[str, Any] | None = None,
    execution_token: str | None = None,
    allow_direct_tool_execute: bool = False,
) -> dict[str, Any]:
    """Return a route decision + proposal drafts. Direct tool execute forbidden."""
    del goal, plan  # binding reserved for fuller impl
    ctx = routing_context or {}
    if allow_direct_tool_execute:
        raise OrchestrationError("direct tool execute forbidden; Authority+Gateway required")

    cost_remaining = ctx.get("cost_remaining")
    if cost_remaining is not None and float(cost_remaining) <= 0:
        return {
            "decision": "BUDGET_EXCEEDED",
            "handoff_to": "stop_or_escalate",
            "cost_ledger_delta": {"usd": 0, "tokens": 0},
        }

    risk = str(ctx.get("risk") or "low")
    model_tier = "heavy_reasoner" if risk in {"high", "material"} else "cheap_fast"
    tool_ids = list(ctx.get("tool_ids") or ["filesystem.read"])

    proposal_draft = {
        "proposal_id": f"ap_route_{task.get('task_id', 'unknown')}",
        "capability": tool_ids[0] if tool_ids else "filesystem.read",
        "requires_execution_token": True,
        "execution_token_present": bool(execution_token),
    }
    if not execution_token:
        # Still return route, but mark not executable until Authority mints token
        handoff = "authority_kernel"
    else:
        handoff = "tool_gateway"

    return {
        "decision": "ROUTE",
        "model_tier": model_tier,
        "tool_ids": tool_ids,
        "estimated_cost": {"usd": float(ctx.get("est_usd") or 0.01), "tokens": int(ctx.get("est_tokens") or 1000)},
        "rationale_code": f"tier_{model_tier}_risk_{risk}",
        "action_proposal_drafts": [proposal_draft],
        "cost_ledger_delta": {"usd": 0, "tokens": 0, "reserved": True},
        "handoff_to": handoff,
        "world_success_claimed": False,
    }
