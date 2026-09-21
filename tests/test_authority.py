from __future__ import annotations

import pytest

from global_os.kernel.action_gateway import MissingExecutionToken, ToolGateway, ToolResult
from global_os.kernel.authority import AuthorityKernel, Decision
from global_os.runtime.events import EventLedger


def test_child_cannot_exceed_parent_grant():
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    auth.grant(
        principal_id="manager",
        capabilities={"web.read", "email.draft"},
        tenant_id="t",
        workspace_id="w",
    )
    with pytest.raises(ValueError, match="GOS-I04"):
        auth.grant(
            principal_id="worker",
            capabilities={"web.read", "email.send"},
            parent_id="manager",
            tenant_id="t",
            workspace_id="w",
        )


def test_denied_action_never_reaches_tool(sample_proposal):
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    gateway = ToolGateway(ledger)
    gateway.register_tool("web.fetch", lambda p: ToolResult(True, {}))

    auth.grant(
        principal_id="worker_research_1",
        capabilities={"filesystem.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(capability="email.send", parent_capabilities=["filesystem.read"])
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert result.decision == Decision.DENY
    assert result.execution_token is None

    with pytest.raises(MissingExecutionToken):
        gateway.execute(
            tool_id="web.fetch",
            proposal=proposal,
            execution_token=result.execution_token,
            tenant_id="t",
            workspace_id="w",
            intended_effect="page_fetched",
        )


def test_allow_issues_token_and_effect_receipt(sample_proposal):
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    gateway = ToolGateway(ledger)
    gateway.register_tool("web.fetch", lambda p: ToolResult(True, {"bytes": 10}))

    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read", "filesystem.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal()
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert result.decision == Decision.ALLOW
    assert result.execution_token
    gateway.accept_token(result.execution_token)

    receipt = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=result.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},
    )
    assert receipt["discrepancy"] == "none"
    assert receipt["tool_response"]["success"] is True

    with pytest.raises(MissingExecutionToken):
        gateway.execute(
            tool_id="web.fetch",
            proposal={**proposal, "idempotency_key": "idem-other"},
            execution_token=result.execution_token,
            tenant_id="t",
            workspace_id="w",
            intended_effect="page_fetched",
        )


def test_idempotency_single_effect(sample_proposal):
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    gateway = ToolGateway(ledger)
    calls = {"n": 0}

    def handler(_p):
        calls["n"] += 1
        return ToolResult(True, {})

    gateway.register_tool("web.fetch", handler)
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(idempotency_key="idem-dup-1", parent_capabilities=["web.read"])
    r1 = auth.decide(proposal, tenant_id="t", workspace_id="w")
    gateway.accept_token(r1.execution_token)
    receipt1 = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=r1.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},
    )
    r2 = auth.decide(
        {**proposal, "proposal_id": "ap_canary_002"},
        tenant_id="t",
        workspace_id="w",
    )
    gateway.accept_token(r2.execution_token)
    receipt2 = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=r2.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},
    )
    assert receipt1["receipt_id"] == receipt2["receipt_id"]
    assert calls["n"] == 1


def test_authority_kernel_rust_backend(sample_proposal):
    from global_os.adapters.authority import find_gos_authority_bin

    if find_gos_authority_bin() is None:
        pytest.skip("gos-authority not built")
    ledger = EventLedger()
    auth = AuthorityKernel(ledger, backend="rust")
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read", "filesystem.read"},
        tenant_id="t",
        workspace_id="w",
    )
    allowed = auth.decide(sample_proposal(), tenant_id="t", workspace_id="w")
    assert allowed.decision == Decision.ALLOW
    assert allowed.execution_token
    denied = auth.decide(
        sample_proposal(capability="email.send", parent_capabilities=["filesystem.read"]),
        tenant_id="t",
        workspace_id="w",
    )
    assert denied.decision == Decision.DENY
    events = ledger.list_events()
    assert any(e["payload"].get("backend") == "rust" for e in events)
