from __future__ import annotations

import pytest

from global_os.epistemic import EpistemicStore
from global_os.runtime.events import EventLedger
from global_os.verification import EvidenceCandidateError, EvidenceCandidatePipeline


def test_tool_trace_is_candidate_not_verified_fact():
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    pipe = EvidenceCandidatePipeline(ledger, epi)
    cand = pipe.ingest_execution_trace(
        goal_id="goal_x",
        origin="tool_result",
        payload={"tool": "database.query", "result": 42},
        tenant_id="t",
        workspace_id="w",
        tool_name="database.query",
        summary="query returned 42",
    )
    assert cand["status"] == "CANDIDATE"
    # raw tool success must not auto-verify
    with pytest.raises(EvidenceCandidateError, match="SYSTEM_TRUSTED"):
        pipe.promote_after_verification(
            cand["candidate_id"],
            verification_status="RUNTIME_VERIFIED",
            trust_label="SYSTEM_TRUSTED",
            tenant_id="t",
            workspace_id="w",
        )
    evidence = pipe.promote_after_verification(
        cand["candidate_id"],
        verification_status="SOURCE_CONTENT_VERIFIED",
        trust_label="EXTERNAL_UNTRUSTED",
        tenant_id="t",
        workspace_id="w",
    )
    assert evidence["status"] == "SOURCE_CONTENT_VERIFIED"
    assert pipe.get(cand["candidate_id"])["status"] == "PROMOTED"
    assert epi.get_evidence(evidence["evidence_id"])["evidence_id"] == evidence["evidence_id"]


def test_reasoning_trace_cannot_become_candidate():
    pipe = EvidenceCandidatePipeline(EventLedger(), EpistemicStore(EventLedger()))
    with pytest.raises(EvidenceCandidateError, match="GOS-I21"):
        pipe.ingest_execution_trace(
            goal_id="goal_x",
            origin="reasoning_trace",
            payload={"cot": "because I think so"},
            tenant_id="t",
            workspace_id="w",
        )


def test_unverified_status_cannot_promote():
    ledger = EventLedger()
    pipe = EvidenceCandidatePipeline(ledger, EpistemicStore(ledger))
    cand = pipe.ingest_execution_trace(
        goal_id="goal_x",
        origin="effect_receipt",
        payload={"receipt": "ok"},
        tenant_id="t",
        workspace_id="w",
    )
    with pytest.raises(EvidenceCandidateError, match="UNVERIFIED"):
        pipe.promote_after_verification(
            cand["candidate_id"],
            verification_status="UNVERIFIED",
            trust_label="EXTERNAL_UNTRUSTED",
            tenant_id="t",
            workspace_id="w",
        )
