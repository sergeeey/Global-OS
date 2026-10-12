"""P0b: deterministic ConfirmPolicy — no LLM security (ADR-0013)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from global_os.common.hashing import content_hash
from global_os.kernel.action_gateway.gateway import ToolGateway, ToolResult
from global_os.kernel.authority import memory_approval_service
from global_os.kernel.policy.confirm import (
    ConfirmationPolicy,
    ConfirmationRequired,
    SecurityRisk,
    assess_action_risk,
    enforce_confirmation,
)
from global_os.runtime.events.ledger import EventLedger


def test_assessment_ignores_llm_security_risk_field() -> None:
    # LLM claims LOW but tool is shell.exec → deterministic HIGH
    a = assess_action_risk(
        {"tool_id": "shell.exec", "security_risk": "LOW", "llm_security_risk": "LOW"}
    )
    assert a.risk is SecurityRisk.HIGH
    assert a.source == "deterministic_policy"


def test_confirm_risky_blocks_high_without_approval() -> None:
    with pytest.raises(ConfirmationRequired):
        enforce_confirmation(
            {"tool_id": "shell.exec"},
            ConfirmationPolicy.CONFIRM_RISKY,
            approval_present=False,
        )


def test_confirm_risky_allows_high_with_approval() -> None:
    a = enforce_confirmation(
        {"tool_id": "shell.exec"},
        ConfirmationPolicy.CONFIRM_RISKY,
        approval_present=True,
    )
    assert a.risk is SecurityRisk.HIGH


def test_gateway_confirm_gate_before_execute() -> None:
    ledger = EventLedger()
    approvals = memory_approval_service()
    gw = ToolGateway(
        ledger,
        confirmation_policy=ConfirmationPolicy.CONFIRM_RISKY,
        allow_legacy_tokens=True,
        approval_service=approvals,
    )
    called = {"n": 0}

    def _tool(_p: dict) -> ToolResult:
        called["n"] += 1
        return ToolResult(True, {})

    gw.register_tool("shell.exec", _tool, required_capabilities=("shell.exec",))
    gw.accept_token("legacy_confirm_tok")
    proposal = {
        "goal_id": "g1",
        "principal_id": "p1",
        "idempotency_key": "idem-1",
        "capability": "shell.exec",
        "resource": "local",
        "args": {},
    }
    with pytest.raises(ConfirmationRequired):
        gw.execute(
            tool_id="shell.exec",
            proposal=proposal,
            execution_token="legacy_confirm_tok",
            tenant_id="t",
            workspace_id="w",
            intended_effect="ran",
        )
    assert called["n"] == 0

    # Bare approval_present bool is insufficient
    gw.accept_token("legacy_confirm_tok2")
    proposal2 = {**proposal, "idempotency_key": "idem-2"}
    with pytest.raises(ConfirmationRequired):
        gw.execute(
            tool_id="shell.exec",
            proposal=proposal2,
            execution_token="legacy_confirm_tok2",
            tenant_id="t",
            workspace_id="w",
            intended_effect="ran",
            approval_present=True,
        )
    assert called["n"] == 0

    # Verified ApprovalToken allows execute
    gw.accept_token("legacy_confirm_tok3")
    proposal3 = {**proposal, "idempotency_key": "idem-3", "tool_id": "shell.exec"}
    action_hash = content_hash({k: v for k, v in proposal3.items() if k != "approval_token"})
    token = approvals.issue(
        approver="human",
        action_hash=action_hash,
        goal_id="g1",
        limits={},
        valid_until=(datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    )
    proposal3 = {**proposal3, "approval_token": token.to_dict()}
    receipt = gw.execute(
        tool_id="shell.exec",
        proposal=proposal3,
        execution_token="legacy_confirm_tok3",
        tenant_id="t",
        workspace_id="w",
        intended_effect="ran",
        observation={"effect": "ran"},
    )
    assert called["n"] == 1
    assert receipt.get("world_success") is True
