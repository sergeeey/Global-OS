"""Evidence candidate pipeline — Execution Trace → Candidate → Verification → Epistemic status (GOS-I22)."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.epistemic.store import EpistemicStore
from global_os.runtime.events.ledger import EventLedger

FORBIDDEN_ORIGINS = frozenset({"reasoning_trace", "chain_of_thought", "model_self_report"})


class EvidenceCandidateError(Exception):
    pass


class EvidenceCandidatePipeline:
    """Tool/runtime outputs become candidates only — never auto-VERIFIED facts."""

    def __init__(self, ledger: EventLedger, epistemic: EpistemicStore) -> None:
        self._ledger = ledger
        self._epistemic = epistemic
        self._candidates: dict[str, dict[str, Any]] = {}

    def ingest_execution_trace(
        self,
        *,
        goal_id: str,
        origin: str,
        payload: dict[str, Any],
        tenant_id: str,
        workspace_id: str,
        task_id: str | None = None,
        tool_name: str | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        if origin in FORBIDDEN_ORIGINS or origin.startswith("reasoning"):
            raise EvidenceCandidateError(
                "reasoning/CoT cannot become evidence candidate (GOS-I21/I22)"
            )
        allowed = {
            "tool_result",
            "effect_receipt",
            "runtime_artifact",
            "external_observation",
            "measurement",
            "test_report",
        }
        if origin not in allowed:
            raise EvidenceCandidateError(f"unsupported candidate origin: {origin}")

        now = datetime.now(UTC).isoformat()
        candidate: dict[str, Any] = {
            "candidate_id": new_id("ecand"),
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "task_id": task_id,
            "status": "CANDIDATE",
            "origin": origin,
            "tool_name": tool_name,
            "raw_ref": payload.get("raw_ref"),
            "summary": summary or payload.get("summary"),
            "content_digest": content_hash(payload),
            "recorded_at": now,
        }
        candidate = {k: v for k, v in candidate.items() if v is not None}
        validate(candidate, "evidence_candidate.schema.json")
        self._candidates[candidate["candidate_id"]] = candidate
        self._ledger.append(
            event_type="evidence.candidate_recorded",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            task_id=task_id,
            payload={"candidate_id": candidate["candidate_id"], "origin": origin},
            producer="verification.evidence_candidate",
        )
        return deepcopy(candidate)

    def reject(
        self,
        candidate_id: str,
        *,
        reason: str,
        tenant_id: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        cand = self._candidates[candidate_id]
        if cand["status"] != "CANDIDATE":
            raise EvidenceCandidateError(f"cannot reject status={cand['status']}")
        cand["status"] = "REJECTED"
        cand["rejection_reason"] = reason
        self._ledger.append(
            event_type="evidence.candidate_rejected",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=cand.get("goal_id"),
            payload={"candidate_id": candidate_id, "reason": reason},
            producer="verification.evidence_candidate",
        )
        return deepcopy(cand)

    def promote_after_verification(
        self,
        candidate_id: str,
        *,
        verification_status: str,
        trust_label: str,
        tenant_id: str,
        workspace_id: str,
    ) -> dict[str, Any]:
        """Promote only after an explicit verification status — never from raw tool success."""
        cand = self._candidates[candidate_id]
        if cand["status"] != "CANDIDATE":
            raise EvidenceCandidateError(f"cannot promote status={cand['status']}")
        if verification_status in {"UNVERIFIED", "INVALIDATED", "STALE", "CONTRADICTED"}:
            raise EvidenceCandidateError(
                f"cannot promote with verification_status={verification_status}"
            )
        if trust_label == "SYSTEM_TRUSTED" and cand["origin"] == "tool_result":
            # tool result alone cannot be SYSTEM_TRUSTED world fact
            raise EvidenceCandidateError(
                "tool_result cannot promote to SYSTEM_TRUSTED without stronger verification (GOS-I22)"
            )

        now = datetime.now(UTC).isoformat()
        evidence = {
            "evidence_id": new_id("ev"),
            "schema_version": "0.1.0",
            "goal_id": cand["goal_id"],
            "status": verification_status,
            "trust_label": trust_label,
            "recorded_at": now,
            "known_at": now,
            "content_digest": cand["content_digest"],
            "source_ref": cand.get("raw_ref") or cand.get("tool_name"),
            "summary": cand.get("summary"),
        }
        evidence = {k: v for k, v in evidence.items() if v is not None}
        self._epistemic.put_evidence(evidence)
        cand["status"] = "PROMOTED"
        cand["promoted_evidence_id"] = evidence["evidence_id"]
        self._ledger.append(
            event_type="evidence.candidate_promoted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=cand.get("goal_id"),
            payload={
                "candidate_id": candidate_id,
                "evidence_id": evidence["evidence_id"],
                "verification_status": verification_status,
            },
            producer="verification.evidence_candidate",
        )
        return deepcopy(evidence)

    def get(self, candidate_id: str) -> dict[str, Any]:
        return deepcopy(self._candidates[candidate_id])
