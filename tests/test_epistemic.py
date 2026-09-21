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
    stale = epi.invalidate_evidence(
        "ev_001", tenant_id="t", workspace_id="w", reason="source withdrawn"
    )
    assert stale == ["cl_001"]
    assert epi.get_claim("cl_001")["status"] == "STALE"
    assert epi.get_evidence("ev_001")["status"] == "INVALIDATED"
