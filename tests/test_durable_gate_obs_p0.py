"""P0 audit: durable jti/idempotency + observation provenance ≠ WorldSuccess."""

from __future__ import annotations

from pathlib import Path

import pytest

from global_os.kernel.action_gateway import (
    EffectReconciliationStatus,
    SqliteDurableGateStore,
    ToolGateway,
    ToolResult,
    reconcile_effect,
    trusted_observation,
)
from global_os.kernel.authority import AuthorityKernel, Decision, ExecutionTokenService
from global_os.runtime.events import EventLedger


def test_bare_effect_string_cannot_prove_world_success() -> None:
    status, observed, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation={"effect": "paid"},
    )
    assert status == EffectReconciliationStatus.DISCREPANCY
    assert observed == "paid"
    assert disc == "untrusted_observation_provenance"


def test_trusted_observation_can_reconcile() -> None:
    status, observed, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation=trusted_observation("paid"),
    )
    assert status == EffectReconciliationStatus.RECONCILED
    assert observed == "paid"
    assert disc == "none"


def test_model_claim_source_rejected() -> None:
    status, _, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation={
            "effect": "paid",
            "source": "model_claim",
            "method": "llm_said_so",
        },
    )
    assert status == EffectReconciliationStatus.DISCREPANCY
    assert disc == "untrusted_observation_provenance"


def test_forged_allowlisted_source_without_attestation_rejected() -> None:
    """Adversarial: attacker copies source=gateway_probe without HMAC."""
    forged = {
        "effect": "paid",
        "source": "gateway_probe",
        "method": "deterministic_probe",
        "provenance": {
            "source": "gateway_probe",
            "method": "deterministic_probe",
        },
        # no attestation
    }
    status, _, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation=forged,
    )
    assert status == EffectReconciliationStatus.DISCREPANCY
    assert disc == "untrusted_observation_provenance"


def test_forged_allowlisted_source_with_bogus_attestation_rejected() -> None:
    forged = {
        "effect": "paid",
        "source": "gateway_probe",
        "method": "deterministic_probe",
        "provenance": {
            "source": "gateway_probe",
            "method": "deterministic_probe",
        },
        "attestation": "not-a-valid-hmac",
    }
    status, _, disc = reconcile_effect(
        tool_success=True,
        intended_effect="paid",
        observation=forged,
    )
    assert status == EffectReconciliationStatus.DISCREPANCY
    assert disc == "untrusted_observation_provenance"


def test_strict_profile_rejects_memory_gate_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from global_os.kernel.action_gateway import (
        MemoryDurableGateStore,
        ToolGatewayError,
        require_durable_gate_store,
    )

    monkeypatch.setenv("GOS_REQUIRE_DURABLE_GATE", "1")
    with pytest.raises(ToolGatewayError, match="non-durable"):
        require_durable_gate_store(MemoryDurableGateStore())


def test_strict_profile_rejects_sqlite_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from global_os.kernel.action_gateway import ToolGatewayError, require_durable_gate_store

    monkeypatch.setenv("GOS_REQUIRE_DURABLE_GATE", "1")
    with pytest.raises(ToolGatewayError, match="non-durable"):
        require_durable_gate_store(SqliteDurableGateStore(":memory:"))


def test_strict_profile_accepts_on_disk_sqlite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from global_os.kernel.action_gateway import require_durable_gate_store

    monkeypatch.setenv("GOS_REQUIRE_DURABLE_GATE", "1")
    store = SqliteDurableGateStore(tmp_path / "strict.sqlite")
    require_durable_gate_store(store)  # must not raise
    store.close()


def test_strict_gateway_default_requires_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from global_os.kernel.action_gateway import ToolGateway, ToolGatewayError

    monkeypatch.setenv("GOS_REQUIRE_DURABLE_GATE", "1")
    monkeypatch.delenv("GOS_DURABLE_GATE_PATH", raising=False)
    with pytest.raises(ToolGatewayError, match="GOS_DURABLE_GATE_PATH"):
        ToolGateway(EventLedger())


def test_jti_replay_survives_process_restart(tmp_path: Path, sample_proposal) -> None:
    db = tmp_path / "gate.sqlite"
    store1 = SqliteDurableGateStore(db)
    tokens1 = ExecutionTokenService(gate_store=store1)
    ledger = EventLedger()
    auth = AuthorityKernel(ledger, token_service=tokens1)
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(
        capability="web.read",
        parent_capabilities=["web.read"],
        idempotency_key="idem-dur-jti-1",
    )
    allowed = auth.decide(proposal, tenant_id="t", workspace_id="w")
    assert allowed.decision == Decision.ALLOW
    bearer = allowed.execution_token
    assert bearer
    tokens1.verify_and_consume(bearer, proposal=proposal)
    store1.close()

    # New process: same sqlite path — replay must fail
    store2 = SqliteDurableGateStore(db)
    tokens2 = ExecutionTokenService(gate_store=store2)
    from global_os.kernel.authority.execution_token import ExecutionTokenReplay

    with pytest.raises(ExecutionTokenReplay):
        tokens2.verify_and_consume(bearer, proposal=proposal)
    store2.close()


def test_idempotency_survives_restart_no_double_handler(
    tmp_path: Path, sample_proposal
) -> None:
    db = tmp_path / "gate_idem.sqlite"
    store = SqliteDurableGateStore(db)
    tokens = ExecutionTokenService(gate_store=store)
    ledger = EventLedger()
    auth = AuthorityKernel(ledger, token_service=tokens)
    gateway = ToolGateway(ledger, token_service=tokens, gate_store=store)
    calls = {"n": 0}

    def _handler(_p: dict) -> ToolResult:
        calls["n"] += 1
        return ToolResult(True, {"ok": True})

    gateway.register_tool(
        "web.fetch", _handler, required_capabilities=("web.read",)
    )
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    p1 = sample_proposal(
        capability="web.read",
        parent_capabilities=["web.read"],
        idempotency_key="idem-dur-restart-1",
    )
    a1 = auth.decide(p1, tenant_id="t", workspace_id="w")
    r1 = gateway.execute(
        tool_id="web.fetch",
        proposal=p1,
        execution_token=a1.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation=trusted_observation("page_fetched"),
    )
    assert r1["world_success"] is True
    assert calls["n"] == 1
    store.close()

    # Crash/restart: new services, same durable DB
    store2 = SqliteDurableGateStore(db)
    tokens2 = ExecutionTokenService(gate_store=store2)
    ledger2 = EventLedger()
    auth2 = AuthorityKernel(ledger2, token_service=tokens2)
    gateway2 = ToolGateway(ledger2, token_service=tokens2, gate_store=store2)
    calls2 = {"n": 0}

    def _handler2(_p: dict) -> ToolResult:
        calls2["n"] += 1
        return ToolResult(True, {"ok": True})

    gateway2.register_tool(
        "web.fetch", _handler2, required_capabilities=("web.read",)
    )
    auth2.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    p2 = {
        **p1,
        "proposal_id": "ap_retry_after_crash",
    }
    a2 = auth2.decide(p2, tenant_id="t", workspace_id="w")
    r2 = gateway2.execute(
        tool_id="web.fetch",
        proposal=p2,
        execution_token=a2.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation=trusted_observation("page_fetched"),
    )
    assert calls2["n"] == 0  # handler must not re-run
    assert r2["receipt_id"] == r1["receipt_id"]
    store2.close()


def test_gateway_rejects_bare_observation_as_world_success(
    sample_proposal,
) -> None:
    ledger = EventLedger()
    tokens = ExecutionTokenService()
    auth = AuthorityKernel(ledger, token_service=tokens)
    gateway = ToolGateway(ledger, token_service=tokens)
    gateway.register_tool(
        "web.fetch",
        lambda _p: ToolResult(True, {}),
        required_capabilities=("web.read",),
    )
    auth.grant(
        principal_id="worker_research_1",
        capabilities={"web.read"},
        tenant_id="t",
        workspace_id="w",
    )
    proposal = sample_proposal(
        capability="web.read",
        parent_capabilities=["web.read"],
        idempotency_key="idem-bare-obs",
    )
    allowed = auth.decide(proposal, tenant_id="t", workspace_id="w")
    receipt = gateway.execute(
        tool_id="web.fetch",
        proposal=proposal,
        execution_token=allowed.execution_token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="page_fetched",
        observation={"effect": "page_fetched"},  # caller-asserted only
    )
    assert receipt["tool_response"]["success"] is True
    assert receipt["world_success"] is False
    assert receipt["discrepancy"] == "untrusted_observation_provenance"
