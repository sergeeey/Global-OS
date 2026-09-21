"""Tool Gateway — physically rejects actions without execution token."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class ToolGatewayError(Exception):
    pass


class MissingExecutionToken(ToolGatewayError):
    pass


class DeniedActionReachedGateway(ToolGatewayError):
    """Raised when a DENY path somehow reaches the gateway — invariant break."""


@dataclass
class ToolResult:
    success: bool
    payload: dict[str, Any]


ToolHandler = Callable[[dict[str, Any]], ToolResult]


class ToolGateway:
    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._tools: dict[str, ToolHandler] = {}
        self._valid_tokens: set[str] = set()
        self._idempotency: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool_id: str, handler: ToolHandler) -> None:
        self._tools[tool_id] = handler

    def accept_token(self, token: str) -> None:
        """Authority Kernel deposits ALLOW tokens here."""
        self._valid_tokens.add(token)

    def execute(
        self,
        *,
        tool_id: str,
        proposal: dict[str, Any],
        execution_token: str | None,
        tenant_id: str,
        workspace_id: str,
        intended_effect: str,
        observation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not execution_token:
            raise MissingExecutionToken("Tool Gateway requires execution token (GOS-I03)")
        if execution_token not in self._valid_tokens:
            raise MissingExecutionToken("invalid or already consumed execution token")

        # one-time tokens
        self._valid_tokens.discard(execution_token)

        idem = proposal["idempotency_key"]
        if idem in self._idempotency:
            return self._idempotency[idem]

        handler = self._tools.get(tool_id)
        if handler is None:
            raise ToolGatewayError(f"unknown tool: {tool_id}")

        result = handler(proposal)
        action_id = new_id("act")
        self._ledger.append(
            event_type="action.executed",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload={
                "action_id": action_id,
                "tool_id": tool_id,
                "success": result.success,
                "idempotency_key": idem,
            },
            producer="kernel.action_gateway",
        )

        observed = (observation or {}).get("effect", "unobserved")
        discrepancy = (
            "none" if observed == intended_effect else f"expected={intended_effect} got={observed}"
        )
        receipt = {
            "receipt_id": new_id("er"),
            "schema_version": "0.1.0",
            "action_id": action_id,
            "tool_response": {"success": result.success},
            "intended_effect": intended_effect,
            "observed_effect": observed,
            "discrepancy": discrepancy,
            "verified_at": datetime.now(UTC).isoformat(),
            "verification_method": "observation_method" if observation else "tool_response_only",
        }
        validate(receipt, "effect_receipt.schema.json")
        self._ledger.append(
            event_type="effect.receipted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload=receipt,
            producer="kernel.action_gateway",
        )
        self._idempotency[idem] = receipt
        return receipt
