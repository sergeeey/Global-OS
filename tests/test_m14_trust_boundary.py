"""M1.4 Trust Boundary Hardening — acceptance tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from global_os.common.hashing import content_hash
from global_os.epistemic import EpistemicError, EpistemicStore
from global_os.kernel.action_gateway import (
    EffectReconciliationStatus,
    MissingExecutionToken,
    ToolGateway,
    ToolResult,
    reconcile_effect,
)
from global_os.kernel.authority import (
    AuthorityKernel,
    Decision,
    ExecutionTokenService,
    memory_approval_service,
)
from global_os.runtime.events import EventLedger


def test_execution_token_bound_to_proposal_and_consumed(sample_proposal):
    ledger = EventLedger()
    tokens = ExecutionTokenService(signing_key=b"m14-test-key")
    auth = AuthorityKernel(ledger, token_service=tokens)
    gateway = ToolGateway(ledger, token_service=tokens)
    gateway.register_tool("web.fetch", lambda _p: ToolResult(True, {}))
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(parent_capabilities=["web.read"])
    allowed = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert allowed.decision == Decision.ALLOW
    assert allowed.execution_token.startswith("et1.")

    bad = {**proposal, "resource": "https://evil.example"}
    with pytest.raises(MissingExecutionToken):
        gateway.execute(
            tool_id="web.fetch",
            proposal=bad,
            execution_token=allowed.execution_token,
            tenant_id="t",
            workspace_id="w",
            intended_effect="page_fetched",
            observation={"effect": "page_fetched"},
        )

    allowed2_proposal = {
        **proposal,
        "proposal_id": "ap_canary_010",
        "idempotency_key": "idem-canary-010",
    }
    allowed2 = auth.decide(allowed2_proposal, tenant_id="t", workspace_id="w")
    receipt = gateway.execute(
        tool_id="web.fetch",
        proposal=allowed2_proposal,
        execution_token=allowed2.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},
    )
    assert receipt["reconciliation_status"] == EffectReconciliationStatus.RECONCILED.value


def test_ledger_never_stores_raw_bearer(sample_proposal):
    ledger = EventLedger()
    auth = AuthorityKernel(ledger)
    proposal = sample_proposal(parent_capabilities=["web.read"])
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    result = auth.decide(proposal, tenant_id="t", workspace_id="w")
    blob = json.dumps(ledger.list_events())
    assert result.execution_token not in blob
    assert "execution_token_id" in blob
    assert "execution_token_hash" in blob


def test_approval_id_string_alone_insufficient(sample_proposal):
    ledger = EventLedger()
    approvals = memory_approval_service(b"m14-apr")
    auth = AuthorityKernel(ledger, approval_service=approvals)
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"email.send"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(
        capability="email.send",
        parent_capabilities=["email.send"],
        approval_refs=["apr_forged"],
        intended_effect="email_sent",
        maximum_effect="email_sent",
    )
    pending = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert pending.decision == Decision.PENDING_APPROVAL
    assert pending.execution_token is None


def test_approval_hard_binding_via_verify_and_consume(sample_proposal):
    ledger = EventLedger()
    approvals = memory_approval_service(b"m14-apr2")
    tokens = ExecutionTokenService(signing_key=b"m14-tok2")
    auth = AuthorityKernel(ledger, approval_service=approvals, token_service=tokens)
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"email.send"},
        tenant_id="t",
        workspace_id="w",
    )
    base = sample_proposal(
        capability="email.send",
        parent_capabilities=["email.send"],
        intended_effect="email_sent",
        maximum_effect="email_sent",
        proposal_id="ap_mail_bind",
        idempotency_key="idem-mail-bind",
    )
    ah = content_hash({k: v for k, v in base.items() if k != "approval_token"})
    tok = approvals.issue(
        approver="human_ops",
        action_hash=ah,
        goal_id=base["goal_id"],
        limits={},
        valid_until=(datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        one_time=True,
    )
    allowed = auth.decide({**base, "approval_token": tok.to_dict()}, tenant_id="t", workspace_id="w")
    assert allowed.decision == Decision.ALLOW
    assert allowed.execution_token

    # One-time: replay denied
    again = auth.decide(
        {
            **base,
            "proposal_id": "ap_mail_bind2",
            "idempotency_key": "idem-mail-bind2",
            "approval_token": tok.to_dict(),
        },
        tenant_id="t",
        workspace_id="w",
    )
    assert again.decision == Decision.DENY


def test_claim_evidence_immutable_no_silent_overwrite():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "x"})
    epi.put_evidence(
        {
            "evidence_id": "ev_imm_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "ORG_TRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest,
        }
    )
    with pytest.raises(EpistemicError, match="immutable"):
        epi.put_evidence(
            {
                "evidence_id": "ev_imm_1",
                "schema_version": "0.1.0",
                "goal_id": "goal_x",
                "status": "INVALIDATED",
                "trust_label": "ORG_TRUSTED",
                "recorded_at": now,
                "known_at": now,
                "content_digest": digest,
            }
        )
    epi.put_claim(
        {
            "claim_id": "cl_imm_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "A",
            "status": "ACTIVE",
            "evidence_ids": ["ev_imm_1"],
            "confidence": "MEDIUM",
            "confidence_basis": "test",
            "recorded_at": now,
        }
    )
    with pytest.raises(EpistemicError, match="immutable"):
        epi.put_claim(
            {
                "claim_id": "cl_imm_1",
                "schema_version": "0.1.0",
                "goal_id": "goal_x",
                "statement": "B overwritten",
                "status": "ACTIVE",
                "evidence_ids": ["ev_imm_1"],
                "confidence": "HIGH",
                "confidence_basis": "test",
                "recorded_at": now,
            }
        )


def test_cold_restart_epistemic_graph_and_invalidation():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "lead 90d"})
    epi.put_observation(
        {
            "observation_id": "obs_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "sensor reading",
            "trust_label": "ORG_TRUSTED",
            "source_ref": "sensor:1",
            "recorded_at": now,
            "observed_at": now,
            "known_at": now,
            "content_digest": digest,
        }
    )
    epi.put_evidence(
        {
            "evidence_id": "ev_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "ORG_TRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest,
        }
    )
    epi.put_claim(
        {
            "claim_id": "cl_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Lead time 90d",
            "status": "ACTIVE",
            "evidence_ids": ["ev_cr_1"],
            "confidence": "MEDIUM",
            "confidence_basis": "ops",
            "recorded_at": now,
        }
    )
    epi.put_belief(
        {
            "belief_id": "bel_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "believe lead time",
            "status": "ACTIVE",
            "derived_from_observation_ids": ["obs_cr_1"],
            "supports_claim_ids": ["cl_cr_1"],
            "confidence": "MEDIUM",
            "confidence_basis": "obs",
            "recorded_at": now,
        }
    )
    epi.put_model(
        {
            "model_id": "mdl_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "lead model",
            "status": "ACTIVE",
            "depends_on_claim_ids": ["cl_cr_1"],
            "recorded_at": now,
        }
    )
    epi.put_forecast(
        {
            "forecast_id": "fc_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "delay likely",
            "status": "ACTIVE",
            "depends_on_model_ids": ["mdl_cr_1"],
            "depends_on_claim_ids": ["cl_cr_1"],
            "recorded_at": now,
        }
    )
    epi.put_decision(
        {
            "decision_id": "edn_cr_1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "order early",
            "status": "ACTIVE",
            "depends_on_claim_ids": ["cl_cr_1"],
            "depends_on_forecast_ids": ["fc_cr_1"],
            "recorded_at": now,
        }
    )

    before = epi.canonical_graph()
    snapshot = ledger.export_snapshot()

    restored_ledger = EventLedger.from_snapshot(snapshot)
    restored = EpistemicStore.restore_from_ledger(restored_ledger)
    assert restored.canonical_graph() == before

    out = restored.invalidate_evidence(
        "ev_cr_1", tenant_id="t", workspace_id="w", reason="source withdrawn"
    )
    assert "cl_cr_1" in out["claims"]
    assert restored.get_claim("cl_cr_1")["status"] == "STALE"
    assert restored.get_model("mdl_cr_1")["status"] == "STALE"
    assert restored.get_forecast("fc_cr_1")["status"] == "STALE"
    assert restored.get_decision("edn_cr_1")["status"] == "NEEDS_REVIEW"

    again = EpistemicStore.restore_from_ledger(
        EventLedger.from_snapshot(restored_ledger.export_snapshot())
    )
    assert again.get_claim("cl_cr_1")["status"] == "STALE"
    assert again.get_evidence("ev_cr_1")["status"] == "INVALIDATED"
    assert again.get_decision("edn_cr_1")["status"] == "NEEDS_REVIEW"


def test_effect_reconciliation_tool_success_not_world_success():
    status, observed, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation={"effect": "unpaid"},
    )
    assert status == EffectReconciliationStatus.DISCREPANCY
    assert observed == "unpaid"
    assert disc != "none"

    pending, _, _ = reconcile_effect(
        tool_success=True, intended_effect="paid", observation=None
    )
    assert pending == EffectReconciliationStatus.OBSERVATION_PENDING

    ledger = EventLedger()
    gateway = ToolGateway(ledger)
    gateway.register_tool("pay", lambda _p: ToolResult(True, {}))
    gateway.accept_token("legacy_tok")
    receipt = gateway.execute(
        tool_id="pay",
        proposal={
            "idempotency_key": "idem-recon-1",
            "goal_id": "goal_x",
            "principal_id": "w1",
        },
        execution_token="legacy_tok",
        tenant_id="t",
        workspace_id="w",
        intended_effect="paid",
        observation={"effect": "unpaid"},
        material=True,
    )
    assert receipt["tool_response"]["success"] is True
    assert receipt["world_success"] is False
    assert receipt["reconciliation_status"] == "ESCALATION_REQUIRED"
