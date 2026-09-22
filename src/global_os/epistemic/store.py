"""Epistemic store — typed nodes + invalidation propagation (GOS-I07/I12/I21)."""

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
        self._models: dict[str, dict[str, Any]] = {}
        self._forecasts: dict[str, dict[str, Any]] = {}
        self._decisions: dict[str, dict[str, Any]] = {}
        self._commitments: dict[str, dict[str, Any]] = {}
        self._assumptions: dict[str, dict[str, Any]] = {}

    def put_evidence(
        self,
        evidence: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        eid = evidence["evidence_id"]
        if eid in self._evidence:
            raise EpistemicError(
                f"evidence_id immutable: {eid}; create a new version instead of overwrite"
            )
        self._evidence[eid] = deepcopy(evidence)
        self._ledger.append(
            event_type="epistemic.evidence.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=evidence.get("goal_id"),
            payload=deepcopy(evidence),
            producer="epistemic.store",
        )

    def put_claim(
        self,
        claim: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        cid = claim["claim_id"]
        if cid in self._claims:
            raise EpistemicError(
                f"claim_id immutable: {cid}; create a new version instead of overwrite"
            )
        self._claims[cid] = deepcopy(claim)
        self._ledger.append(
            event_type="epistemic.claim.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=claim.get("goal_id"),
            payload=deepcopy(claim),
            producer="epistemic.store",
        )

    def put_observation(
        self,
        observation: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(observation, "observation.schema.json")
        if observation["trust_label"] == "SYSTEM_TRUSTED" and observation.get(
            "source_ref", ""
        ).startswith("reasoning:"):
            raise EpistemicError("reasoning trace cannot be SYSTEM_TRUSTED observation (GOS-I21)")
        oid = observation["observation_id"]
        if oid in self._observations:
            raise EpistemicError(f"observation_id immutable: {oid}")
        self._observations[oid] = deepcopy(observation)
        self._ledger.append(
            event_type="epistemic.observation.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=observation.get("goal_id"),
            payload=deepcopy(observation),
            producer="epistemic.store",
        )

    def put_belief(
        self,
        belief: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(belief, "belief.schema.json")
        for obs_id in belief.get("derived_from_observation_ids", []):
            if obs_id not in self._observations:
                raise EpistemicError(f"belief references missing observation: {obs_id}")
        bid = belief["belief_id"]
        if bid in self._beliefs:
            raise EpistemicError(f"belief_id immutable: {bid}")
        self._beliefs[bid] = deepcopy(belief)
        self._ledger.append(
            event_type="epistemic.belief.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=belief.get("goal_id"),
            payload=deepcopy(belief),
            producer="epistemic.store",
        )

    def put_model(
        self,
        model: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(model, "epistemic_model.schema.json")
        for claim_id in model.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"model references missing claim: {claim_id}")
        mid = model["model_id"]
        if mid in self._models:
            raise EpistemicError(f"model_id immutable: {mid}")
        self._models[mid] = deepcopy(model)
        self._ledger.append(
            event_type="epistemic.model.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=model.get("goal_id"),
            payload=deepcopy(model),
            producer="epistemic.store",
        )

    def put_forecast(
        self,
        forecast: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(forecast, "forecast.schema.json")
        for mid in forecast.get("depends_on_model_ids", []):
            if mid not in self._models:
                raise EpistemicError(f"forecast references missing model: {mid}")
        for claim_id in forecast.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"forecast references missing claim: {claim_id}")
        fid = forecast["forecast_id"]
        if fid in self._forecasts:
            raise EpistemicError(f"forecast_id immutable: {fid}")
        self._forecasts[fid] = deepcopy(forecast)
        self._ledger.append(
            event_type="epistemic.forecast.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=forecast.get("goal_id"),
            payload=deepcopy(forecast),
            producer="epistemic.store",
        )

    def put_decision(
        self,
        decision: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(decision, "epistemic_decision.schema.json")
        for claim_id in decision.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"decision references missing claim: {claim_id}")
        for fid in decision.get("depends_on_forecast_ids", []):
            if fid not in self._forecasts:
                raise EpistemicError(f"decision references missing forecast: {fid}")
        did = decision["decision_id"]
        if did in self._decisions:
            raise EpistemicError(f"decision_id immutable: {did}")
        self._decisions[did] = deepcopy(decision)
        self._ledger.append(
            event_type="epistemic.decision.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=decision.get("goal_id"),
            payload=deepcopy(decision),
            producer="epistemic.store",
        )

    def put_commitment(
        self,
        commitment: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(commitment, "commitment.schema.json")
        for claim_id in commitment.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"commitment references missing claim: {claim_id}")
        cid = commitment["commitment_id"]
        if cid in self._commitments:
            raise EpistemicError(f"commitment_id immutable: {cid}")
        self._commitments[cid] = deepcopy(commitment)
        self._ledger.append(
            event_type="epistemic.commitment.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=commitment.get("goal_id"),
            payload=deepcopy(commitment),
            producer="epistemic.store",
        )

    def put_assumption(
        self,
        assumption: dict[str, Any],
        *,
        tenant_id: str = "local",
        workspace_id: str = "local",
    ) -> None:
        validate(assumption, "assumption.schema.json")
        aid = assumption["assumption_id"]
        if aid in self._assumptions:
            raise EpistemicError(f"assumption_id immutable: {aid}")
        self._assumptions[aid] = deepcopy(assumption)
        self._ledger.append(
            event_type="epistemic.assumption.put",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=assumption.get("goal_id"),
            payload=deepcopy(assumption),
            producer="epistemic.store",
        )

    def canonical_graph(self) -> dict[str, Any]:
        """Stable snapshot for cold-restart equality checks."""
        return {
            "evidence": {k: self._evidence[k] for k in sorted(self._evidence)},
            "claims": {k: self._claims[k] for k in sorted(self._claims)},
            "observations": {k: self._observations[k] for k in sorted(self._observations)},
            "beliefs": {k: self._beliefs[k] for k in sorted(self._beliefs)},
            "models": {k: self._models[k] for k in sorted(self._models)},
            "forecasts": {k: self._forecasts[k] for k in sorted(self._forecasts)},
            "decisions": {k: self._decisions[k] for k in sorted(self._decisions)},
            "commitments": {k: self._commitments[k] for k in sorted(self._commitments)},
            "assumptions": {k: self._assumptions[k] for k in sorted(self._assumptions)},
        }

    @classmethod
    def restore_from_ledger(cls, ledger: EventLedger) -> EpistemicStore:
        """Cold-start reconstruction from durable event history only (empty RAM)."""
        store = cls(ledger)
        # Replay without re-appending: load maps directly then skip duplicate ledger writes
        # by using internal hydrate path.
        for event in ledger.list_events():
            et = event.get("event_type", "")
            payload = deepcopy(event.get("payload") or {})
            if et == "epistemic.evidence.put":
                store._evidence[payload["evidence_id"]] = payload
            elif et == "epistemic.claim.put":
                store._claims[payload["claim_id"]] = payload
            elif et == "epistemic.observation.put":
                store._observations[payload["observation_id"]] = payload
            elif et == "epistemic.belief.put":
                store._beliefs[payload["belief_id"]] = payload
            elif et == "epistemic.model.put":
                store._models[payload["model_id"]] = payload
            elif et == "epistemic.forecast.put":
                store._forecasts[payload["forecast_id"]] = payload
            elif et == "epistemic.decision.put":
                store._decisions[payload["decision_id"]] = payload
            elif et == "epistemic.commitment.put":
                store._commitments[payload["commitment_id"]] = payload
            elif et == "epistemic.assumption.put":
                store._assumptions[payload["assumption_id"]] = payload
            elif et == "evidence.invalidated":
                eid = payload.get("evidence_id")
                if eid in store._evidence:
                    store._evidence[eid]["status"] = "INVALIDATED"
            elif et == "claim.staled":
                cid = payload.get("claim_id")
                if cid in store._claims:
                    store._claims[cid]["status"] = "STALE"
            elif et == "claim.contradicted":
                cid = payload.get("claim_id")
                if cid in store._claims:
                    store._claims[cid]["status"] = "CONTRADICTED"
            elif et == "model.staled":
                mid = payload.get("model_id")
                if mid in store._models:
                    store._models[mid]["status"] = "STALE"
            elif et == "forecast.staled":
                fid = payload.get("forecast_id")
                if fid in store._forecasts:
                    store._forecasts[fid]["status"] = "STALE"
            elif et == "decision.staled":
                did = payload.get("decision_id")
                if did in store._decisions:
                    store._decisions[did]["status"] = "STALE"
            elif et == "decision.needs_review":
                did = payload.get("decision_id")
                if did in store._decisions:
                    store._decisions[did]["status"] = "NEEDS_REVIEW"
            elif et == "commitment.staled":
                cid = payload.get("commitment_id")
                if cid in store._commitments:
                    store._commitments[cid]["status"] = "STALE"
            elif et == "commitment.needs_review":
                cid = payload.get("commitment_id")
                if cid in store._commitments:
                    store._commitments[cid]["status"] = "NEEDS_REVIEW"
            elif et == "belief.staled":
                bid = payload.get("belief_id")
                if bid in store._beliefs:
                    store._beliefs[bid]["status"] = "STALE"
            elif et == "assumption.staled":
                aid = payload.get("assumption_id")
                if aid in store._assumptions:
                    store._assumptions[aid]["status"] = "STALE"
        return store

    def get_claim(self, claim_id: str) -> dict[str, Any]:
        return deepcopy(self._claims[claim_id])

    def get_evidence(self, evidence_id: str) -> dict[str, Any]:
        return deepcopy(self._evidence[evidence_id])

    def get_observation(self, observation_id: str) -> dict[str, Any]:
        return deepcopy(self._observations[observation_id])

    def get_belief(self, belief_id: str) -> dict[str, Any]:
        return deepcopy(self._beliefs[belief_id])

    def get_model(self, model_id: str) -> dict[str, Any]:
        return deepcopy(self._models[model_id])

    def get_forecast(self, forecast_id: str) -> dict[str, Any]:
        return deepcopy(self._forecasts[forecast_id])

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        return deepcopy(self._decisions[decision_id])

    def get_commitment(self, commitment_id: str) -> dict[str, Any]:
        return deepcopy(self._commitments[commitment_id])

    def get_assumption(self, assumption_id: str) -> dict[str, Any]:
        return deepcopy(self._assumptions[assumption_id])

    def mark_contradicted(
        self,
        claim_id: str,
        *,
        evidence_ids: list[str],
        tenant_id: str,
        workspace_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """Two+ conflicting evidence refs → claim CONTRADICTED (GOS-I16). Never auto-VERIFIED."""
        claim = self._claims[claim_id]
        if len(evidence_ids) < 2:
            raise EpistemicError("contradiction requires ≥2 evidence ids")
        for eid in evidence_ids:
            if eid not in self._evidence:
                raise EpistemicError(f"unknown evidence for contradiction: {eid}")
        claim["status"] = "CONTRADICTED"
        claim["evidence_ids"] = list(dict.fromkeys([*claim.get("evidence_ids", []), *evidence_ids]))
        claim["confidence"] = "LOW"
        claim["confidence_basis"] = f"contradictory evidence: {reason}"
        self._ledger.append(
            event_type="claim.contradicted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=claim.get("goal_id"),
            payload={
                "claim_id": claim_id,
                "evidence_ids": evidence_ids,
                "reason": reason,
            },
            producer="epistemic.contradiction",
        )
        downstream = self._propagate_from_claims(
            [claim_id], tenant_id=tenant_id, workspace_id=workspace_id
        )
        return {"claim_id": claim_id, "status": "CONTRADICTED", **downstream}

    def invalidate_evidence(
        self,
        evidence_id: str,
        *,
        tenant_id: str,
        workspace_id: str,
        reason: str,
    ) -> dict[str, list[str]]:
        """Full GOS-I12 chain: evidence → claim → model → forecast → decision → commitment."""
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
            stale_claims, tenant_id=tenant_id, workspace_id=workspace_id
        )
        downstream = self._propagate_from_claims(
            stale_claims, tenant_id=tenant_id, workspace_id=workspace_id
        )
        return {
            "claims": stale_claims,
            "models": downstream["models"],
            "forecasts": downstream["forecasts"],
            "decisions": downstream["decisions"],
            "commitments": downstream["commitments"],
            "assumptions": downstream["assumptions"],
        }

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

        downstream = self._propagate_from_claims(
            stale_claims, tenant_id=tenant_id, workspace_id=workspace_id
        )
        return {
            "beliefs": stale_beliefs,
            "claims": stale_claims,
            "models": downstream["models"],
            "forecasts": downstream["forecasts"],
            "decisions": downstream["decisions"],
            "commitments": downstream["commitments"],
            "assumptions": downstream["assumptions"],
        }

    def _propagate_from_claims(
        self,
        claim_ids: list[str],
        *,
        tenant_id: str,
        workspace_id: str,
    ) -> dict[str, list[str]]:
        claim_set = set(claim_ids)
        stale_models: list[str] = []
        for model in self._models.values():
            if model["status"] != "ACTIVE":
                continue
            deps = set(model.get("depends_on_claim_ids", []))
            if deps & claim_set:
                model["status"] = "STALE"
                stale_models.append(model["model_id"])
                self._ledger.append(
                    event_type="model.staled",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=model.get("goal_id"),
                    payload={
                        "model_id": model["model_id"],
                        "because_claims": sorted(deps & claim_set),
                    },
                    producer="epistemic.invalidation",
                )

        model_set = set(stale_models)
        stale_forecasts: list[str] = []
        for forecast in self._forecasts.values():
            if forecast["status"] != "ACTIVE":
                continue
            mdeps = set(forecast.get("depends_on_model_ids", []))
            cdeps = set(forecast.get("depends_on_claim_ids", []))
            if (mdeps & model_set) or (cdeps & claim_set):
                forecast["status"] = "STALE"
                stale_forecasts.append(forecast["forecast_id"])
                self._ledger.append(
                    event_type="forecast.staled",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=forecast.get("goal_id"),
                    payload={
                        "forecast_id": forecast["forecast_id"],
                        "because_models": sorted(mdeps & model_set),
                        "because_claims": sorted(cdeps & claim_set),
                    },
                    producer="epistemic.invalidation",
                )

        forecast_set = set(stale_forecasts)
        review_decisions: list[str] = []
        for decision in self._decisions.values():
            if decision["status"] != "ACTIVE":
                continue
            cdeps = set(decision.get("depends_on_claim_ids", []))
            fdeps = set(decision.get("depends_on_forecast_ids", []))
            if (cdeps & claim_set) or (fdeps & forecast_set):
                decision["status"] = "NEEDS_REVIEW"
                review_decisions.append(decision["decision_id"])
                self._ledger.append(
                    event_type="decision.needs_review",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=decision.get("goal_id"),
                    payload={
                        "decision_id": decision["decision_id"],
                        "because_claims": sorted(cdeps & claim_set),
                        "because_forecasts": sorted(fdeps & forecast_set),
                    },
                    producer="epistemic.invalidation",
                )

        review_commitments: list[str] = []
        for commitment in self._commitments.values():
            if commitment["status"] != "ACTIVE":
                continue
            cdeps = set(commitment.get("depends_on_claim_ids", []))
            if cdeps & claim_set:
                commitment["status"] = "NEEDS_REVIEW"
                review_commitments.append(commitment["commitment_id"])
                self._ledger.append(
                    event_type="commitment.needs_review",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=commitment.get("goal_id"),
                    payload={
                        "commitment_id": commitment["commitment_id"],
                        "because_claims": sorted(cdeps & claim_set),
                    },
                    producer="epistemic.invalidation",
                )

        stale_assumptions: list[str] = []
        for assumption in self._assumptions.values():
            if assumption["status"] != "ACTIVE":
                continue
            cdeps = set(assumption.get("depends_on_claim_ids", []))
            edeps = set(assumption.get("depends_on_evidence_ids", []))
            evidence_invalid = any(
                eid in self._evidence and self._evidence[eid].get("status") == "INVALIDATED"
                for eid in edeps
            )
            if (cdeps & claim_set) or evidence_invalid:
                assumption["status"] = "STALE"
                stale_assumptions.append(assumption["assumption_id"])
                self._ledger.append(
                    event_type="assumption.staled",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    goal_id=assumption.get("goal_id"),
                    payload={
                        "assumption_id": assumption["assumption_id"],
                        "because_claims": sorted(cdeps & claim_set),
                        "because_evidence": sorted(edeps) if evidence_invalid else [],
                    },
                    producer="epistemic.invalidation",
                )

        return {
            "models": stale_models,
            "forecasts": stale_forecasts,
            "decisions": review_decisions,
            "commitments": review_commitments,
            "assumptions": stale_assumptions,
        }

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
