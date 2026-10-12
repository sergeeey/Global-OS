"""Audit P0 regressions: token↔tool bind, approval_present, parent grants (GOS-I03/I04).

These tests must fail on tip before the fix and pass after.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from global_os.adapters.tools.base import FakePaymentTool, FakeReadTool
from global_os.common.hashing import content_hash
from global_os.kernel.action_gateway import (
    CapabilityToolMismatch,
    ToolGateway,
    ToolResult,
)
from global_os.kernel.authority import AuthorityKernel, Decision, memory_approval_service
from global_os.kernel.authority.execution_token import ExecutionTokenService
from global_os.kernel.policy.confirm import ConfirmationPolicy, ConfirmationRequired
from global_os.runtime.events import EventLedger


def test_web_read_token_cannot_execute_payment_fake(sample_proposal):
    """Finding N1/P1: token for web.read must not run payment.fake (confused deputy)."""
    ledger = EventLedger()
    tokens = ExecutionTokenService()
    auth = AuthorityKernel(ledger, token_service=tokens)
    gateway = ToolGateway(ledger, token_service=tokens)
    pay = FakePaymentTool()
    gateway.register_tool(
        pay.spec().tool_id,
        lambda _p: ToolResult(True, {"paid": True}),
        spec=pay.spec(),
    )

    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(capability="web.read", parent_capabilities=["web.read"])
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert result.decision == Decision.ALLOW
    assert result.execution_token

    with pytest.raises(CapabilityToolMismatch, match="required_capabilities"):
        gateway.execute(
            tool_id="payment.fake",
            proposal=proposal,
            execution_token=result.execution_token,
            tenant_id="t",
            workspace_id="w",
            intended_effect="paid",
        )


def test_matching_capability_still_executes(sample_proposal):
    ledger = EventLedger()
    tokens = ExecutionTokenService()
    auth = AuthorityKernel(ledger, token_service=tokens)
    gateway = ToolGateway(ledger, token_service=tokens)
    read = FakeReadTool()
    gateway.register_tool(
        "web.fetch",
        lambda _p: ToolResult(True, {}),
        required_capabilities=read.spec().required_capabilities,
    )
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal()
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    receipt = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=result.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},
    )
    assert receipt["world_success"] is True


def test_approval_present_bool_alone_does_not_bypass_confirm():
    """Finding: approval_present=True must not skip confirmation without ApprovalToken."""
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
    gw.accept_token("legacy_a")
    proposal = {
        "goal_id": "g1",
        "principal_id": "p1",
        "idempotency_key": "idem-bool",
        "capability": "shell.exec",
        "resource": "local",
        "args": {},
    }
    with pytest.raises(ConfirmationRequired):
        gw.execute(
            tool_id="shell.exec",
            proposal=proposal,
            execution_token="legacy_a",
            tenant_id="t",
            workspace_id="w",
            intended_effect="ran",
            approval_present=True,  # bare bool — insufficient
        )
    assert called["n"] == 0


def test_verified_approval_token_allows_confirm_risky():
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
    gw.accept_token("legacy_b")
    proposal = {
        "goal_id": "g1",
        "principal_id": "p1",
        "idempotency_key": "idem-tok",
        "capability": "shell.exec",
        "resource": "local",
        "args": {},
        "tool_id": "shell.exec",
    }
    action_hash = content_hash({k: v for k, v in proposal.items() if k != "approval_token"})
    token = approvals.issue(
        approver="human",
        action_hash=action_hash,
        goal_id="g1",
        limits={},
        valid_until=(datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    )
    proposal_with = {**proposal, "approval_token": token.to_dict()}
    receipt = gw.execute(
        tool_id="shell.exec",
        proposal=proposal_with,
        execution_token="legacy_b",
        tenant_id="t",
        workspace_id="w",
        intended_effect="ran",
        observation={"effect": "ran"},
    )
    assert called["n"] == 1
    assert receipt["world_success"] is True


def test_forged_parent_capabilities_in_request_ignored(sample_proposal):
    """Finding: forging parent_capabilities must not expand authority (GOS-I04)."""
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="manager",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    auth.grant(
        principal_id="worker",
        capabilities={"web.read"},
        parent_id="manager",
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(
        proposal_id="ap_forge_parent",
        principal_id="worker",
        capability="email.send",
        idempotency_key="idem-parent-forge",
        parent_capabilities=["web.read", "email.send"],  # forged
    )
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert result.decision == Decision.DENY
    assert result.execution_token is None


def test_parent_narrowing_enforced_at_decide_time(sample_proposal):
    """After parent grant shrinks, child cannot use removed capability."""
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="manager",
        capabilities={"web.read", "filesystem.read"},
        tenant_id="t",
        workspace_id="w",
    )
    auth.grant(
        principal_id="worker",
        capabilities={"web.read"},
        parent_id="manager",
        tenant_id="t",
        workspace_id="w",
    )
    # Narrow parent (overwrite grant)
    auth.grant(
        principal_id="manager",
        capabilities={"filesystem.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(
        proposal_id="ap_narrow_parent",
        principal_id="worker",
        capability="web.read",
        idempotency_key="idem-narrow01",
        parent_capabilities=["web.read", "filesystem.read"],  # stale request; ignored
    )
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert result.decision == Decision.DENY
    assert "parent" in result.reason.lower() or "GOS-I04" in result.reason
