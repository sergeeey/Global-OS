"""Minimal invalidation engine (GOS-I12)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.runtime.events.ledger import EventLedger


class EpistemicStore:
    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._evidence: dict[str, dict[str, Any]] = {}
        self._claims: dict[str, dict[str, Any]] = {}

    def put_evidence(self, evidence: dict[str, Any]) -> None:
        self._evidence[evidence["evidence_id"]] = deepcopy(evidence)

    def put_claim(self, claim: dict[str, Any]) -> None:
        self._claims[claim["claim_id"]] = deepcopy(claim)

    def get_claim(self, claim_id: str) -> dict[str, Any]:
        return deepcopy(self._claims[claim_id])

    def get_evidence(self, evidence_id: str) -> dict[str, Any]:
        return deepcopy(self._evidence[evidence_id])

    def invalidate_evidence(
        self,
        evidence_id: str,
        *,
        tenant_id: str,
        workspace_id: str,
        reason: str,
    ) -> list[str]:
        ev = self._evidence[evidence_id]
        ev["status"] = "INVALIDATED"
        self._ledger.append(
            event_type="evidence.invalidated",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=ev.get("goal_id"),
            payload={"evidence_id": evidence_id, "reason": reason},
            producer="epistemic.invalidation",
        )
        stale_claims: list[str] = []
        for claim in self._claims.values():
            if evidence_id in claim.get("evidence_ids", []) and claim["status"] == "ACTIVE":
                claim["status"] = "STALE"
                stale_claims.append(claim["claim_id"])
                self._ledger.append(
                    event_type="claim.staled",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=claim.get("goal_id"),
                    payload={
                        "claim_id": claim["claim_id"],
                        "because_evidence": evidence_id,
                    },
                    producer="epistemic.invalidation",
                )
        return stale_claims
