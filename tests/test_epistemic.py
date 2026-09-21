from __future__ import annotations

from datetime import UTC, datetime

from global_os.common.hashing import content_hash
from global_os.epistemic import EpistemicStore
from global_os.runtime.events import EventLedger


def test_invalidation_marks_claim_stale():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "supplier lead time 90d"})
    epi.put_evidence(
        {
            "evidence_id": "ev_001",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "EXTERNAL_UNTRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest,
        }
    )
    epi.put_claim(
        {
            "claim_id": "cl_001",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Lead time is 90 days",
            "status": "ACTIVE",
            "evidence_ids": ["ev_001"],
            "confidence": "MEDIUM",
            "confidence_basis": "single source",
            "recorded_at": now,
        }
    )
    result = epi.invalidate_evidence(
        "ev_001", tenant_id="t", workspace_id="w", reason="source withdrawn"
    )
    assert result["claims"] == ["cl_001"]
    assert epi.get_claim("cl_001")["status"] == "STALE"
    assert epi.get_evidence("ev_001")["status"] == "INVALIDATED"


def test_full_graph_invalidation_model_forecast_decision_commitment():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "demand rising"})
    epi.put_evidence(
        {
            "evidence_id": "ev_d1",
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
            "claim_id": "cl_d1",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Demand is rising",
            "status": "ACTIVE",
            "evidence_ids": ["ev_d1"],
            "confidence": "HIGH",
            "confidence_basis": "ops report",
            "recorded_at": now,
        }
    )
    epi.put_model(
        {
            "model_id": "mdl_demand",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Linear demand growth model",
            "status": "ACTIVE",
            "depends_on_claim_ids": ["cl_d1"],
            "recorded_at": now,
            "confidence": "MEDIUM",
            "confidence_basis": "historical fit",
        }
    )
    epi.put_forecast(
        {
            "forecast_id": "fc_q4",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Q4 volume +12%",
            "status": "ACTIVE",
            "depends_on_model_ids": ["mdl_demand"],
            "recorded_at": now,
            "horizon": "Q4",
        }
    )
    epi.put_decision(
        {
            "decision_id": "edn_hire",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Hire two ops FTE",
            "status": "ACTIVE",
            "depends_on_forecast_ids": ["fc_q4"],
            "depends_on_claim_ids": ["cl_d1"],
            "options": ["hire", "wait"],
            "chosen": "hire",
            "recorded_at": now,
        }
    )
    epi.put_commitment(
        {
            "commitment_id": "com_hire",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Budget reserved for two FTE",
            "status": "ACTIVE",
            "authority_ref": "org_manager",
            "depends_on_claim_ids": ["cl_d1"],
            "recorded_at": now,
        }
    )
    result = epi.invalidate_evidence(
        "ev_d1", tenant_id="t", workspace_id="w", reason="ops report retracted"
    )
    assert result["claims"] == ["cl_d1"]
    assert result["models"] == ["mdl_demand"]
    assert result["forecasts"] == ["fc_q4"]
    assert result["decisions"] == ["edn_hire"]
    assert result["commitments"] == ["com_hire"]
    assert epi.get_model("mdl_demand")["status"] == "STALE"
    assert epi.get_forecast("fc_q4")["status"] == "STALE"
    assert epi.get_decision("edn_hire")["status"] == "NEEDS_REVIEW"
    assert epi.get_commitment("com_hire")["status"] == "NEEDS_REVIEW"
    types = {e["event_type"] for e in ledger.list_events()}
    assert "model.staled" in types
    assert "forecast.staled" in types
    assert "decision.needs_review" in types
    assert "commitment.needs_review" in types
