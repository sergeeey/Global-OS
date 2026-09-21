from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_os.common.hashing import content_hash
from global_os.epistemic import EpistemicError, EpistemicStore
from global_os.runtime.events import EventLedger


def test_observation_belief_separation_and_invalidation():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "CONSTITUTION present"})
    epi.put_observation(
        {
            "observation_id": "obs_001",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "CONSTITUTION.md exists",
            "source_ref": "CONSTITUTION.md",
            "trust_label": "USER_TRUSTED",
            "observed_at": now,
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
            "statement": "Repo documents invariants",
            "status": "ACTIVE",
            "evidence_ids": [],
            "confidence": "MEDIUM",
            "confidence_basis": "belief-supported",
            "recorded_at": now,
        }
    )
    epi.put_belief(
        {
            "belief_id": "bel_001",
            "schema_version": "0.1.0",
            "goal_id": "goal_x",
            "statement": "Invariants are documented",
            "status": "ACTIVE",
            "confidence": "MEDIUM",
            "confidence_basis": "observation obs_001",
            "derived_from_observation_ids": ["obs_001"],
            "supports_claim_ids": ["cl_001"],
            "recorded_at": now,
        }
    )
    result = epi.invalidate_observation(
        "obs_001", tenant_id="t", workspace_id="w", reason="file removed"
    )
    assert result["beliefs"] == ["bel_001"]
    assert result["claims"] == ["cl_001"]
    assert epi.get_belief("bel_001")["status"] == "STALE"
    assert epi.get_claim("cl_001")["status"] == "NEEDS_REVIEW"


def test_reasoning_trace_cannot_be_system_trusted_observation():
    epi = EpistemicStore(EventLedger())
    now = datetime.now(UTC).isoformat()
    with pytest.raises(EpistemicError, match="GOS-I21"):
        epi.put_observation(
            {
                "observation_id": "obs_bad",
                "schema_version": "0.1.0",
                "goal_id": "goal_x",
                "statement": "model thinks X",
                "source_ref": "reasoning:cot",
                "trust_label": "SYSTEM_TRUSTED",
                "observed_at": now,
                "recorded_at": now,
                "known_at": now,
                "content_digest": content_hash({"x": 1}),
            }
        )
