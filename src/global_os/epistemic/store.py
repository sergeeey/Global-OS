"""Epistemic store — Observation ≠ Belief ≠ Claim; invalidation propagates (GOS-I07/I12/I21)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class EpistemicError(Exception):
    pass


class EpistemicStore:
    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._evidence: dict[str, dict[str, Any]] = {}
        self._claims: dict[str, dict[str, Any]] = {}
        self._observations: dict[str, dict[str, Any]] = {}
        self._beliefs: dict[str, dict[str, Any]] = {}

    def put_evidence(self, evidence: dict[str, Any]) -> None:
        self._evidence[evidence["evidence_id"]] = deepcopy(evidence)

    def put_claim(self, claim: dict[str, Any]) -> None:
        self._claims[claim["claim_id"]] = deepcopy(claim)

    def put_observation(self, observation: dict[str, Any]) -> None:
        validate(observation, "observation.schema.json")
        if observation["trust_label"] == "SYSTEM_TRUSTED" and observation.get(
            "source_ref", ""
        ).startswith("reasoning:"):
            raise EpistemicError("reasoning trace cannot be SYSTEM_TRUSTED observation (GOS-I21)")
        self._observations[observation["observation_id"]] = deepcopy(observation)

    def put_belief(self, belief: dict[str, Any]) -> None:
        validate(belief, "belief.schema.json")
        for obs_id in belief.get("derived_from_observation_ids", []):
            if obs_id not in self._observations:
                raise EpistemicError(f"belief references missing observation: {obs_id}")
        self._beliefs[belief["belief_id"]] = deepcopy(belief)

    def get_claim(self, claim_id: str) -> dict[str, Any]:
        return deepcopy(self._claims[claim_id])

    def get_evidence(self, evidence_id: str) -> dict[str, Any]:
        return deepcopy(self._evidence[evidence_id])

    def get_observation(self, observation_id: str) -> dict[str, Any]:
        return deepcopy(self._observations[observation_id])

    def get_belief(self, belief_id: str) -> dict[str, Any]:
        return deepcopy(self._beliefs[belief_id])

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
                self._stale_beliefs_for_claims(
                    [claim["claim_id"]], tenant_id=tenant_id, workspace_id=workspace_id
                )
        return stale_claims

    def invalidate_observation(
        self,
        observation_id: str,
        *,
        tenant_id: str,
        workspace_id: str,
        reason: str,
    ) -> dict[str, list[str]]:
        """Observation invalid → dependent beliefs STALE → linked claims NEEDS_REVIEW."""
        if observation_id not in self._observations:
            raise EpistemicError(f"unknown observation: {observation_id}")
        obs = self._observations[observation_id]
        # Observations don't have status in schema — mark via linked evidence if present
        if obs.get("evidence_id") and obs["evidence_id"] in self._evidence:
            self._evidence[obs["evidence_id"]]["status"] = "INVALIDATED"

        self._ledger.append(
            event_type="evidence.invalidated",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=obs.get("goal_id"),
            payload={
                "observation_id": observation_id,
                "reason": reason,
                "kind": "observation_invalidated",
            },
            producer="epistemic.invalidation",
        )

        stale_beliefs: list[str] = []
        for belief in self._beliefs.values():
            if (
                observation_id in belief.get("derived_from_observation_ids", [])
                and belief["status"] == "ACTIVE"
            ):
                belief["status"] = "STALE"
                stale_beliefs.append(belief["belief_id"])

        stale_claims: list[str] = []
        for belief_id in stale_beliefs:
            belief = self._beliefs[belief_id]
            for claim_id in belief.get("supports_claim_ids", []):
                claim = self._claims.get(claim_id)
                if claim and claim["status"] == "ACTIVE":
                    claim["status"] = "NEEDS_REVIEW"
                    stale_claims.append(claim_id)
                    self._ledger.append(
                        event_type="claim.staled",
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        goal_id=claim.get("goal_id"),
                        payload={
                            "claim_id": claim_id,
                            "because_observation": observation_id,
                            "because_belief": belief_id,
                            "new_status": "NEEDS_REVIEW",
                        },
                        producer="epistemic.invalidation",
                    )

        return {"beliefs": stale_beliefs, "claims": stale_claims}

    def _stale_beliefs_for_claims(
        self, claim_ids: list[str], *, tenant_id: str, workspace_id: str
    ) -> None:
        claim_set = set(claim_ids)
        for belief in self._beliefs.values():
            if belief["status"] != "ACTIVE":
                continue
            supported = set(belief.get("supports_claim_ids", []))
            if supported & claim_set:
                belief["status"] = "STALE"
                self._ledger.append(
                    event_type="claim.staled",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=belief.get("goal_id"),
                    payload={
                        "belief_id": belief["belief_id"],
                        "new_status": "STALE",
                        "because_claims": sorted(supported & claim_set),
                    },
                    producer="epistemic.invalidation",
                )
