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

    def put_model(self, model: dict[str, Any]) -> None:
        validate(model, "epistemic_model.schema.json")
        for claim_id in model.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"model references missing claim: {claim_id}")
        self._models[model["model_id"]] = deepcopy(model)

    def put_forecast(self, forecast: dict[str, Any]) -> None:
        validate(forecast, "forecast.schema.json")
        for mid in forecast.get("depends_on_model_ids", []):
            if mid not in self._models:
                raise EpistemicError(f"forecast references missing model: {mid}")
        for claim_id in forecast.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"forecast references missing claim: {claim_id}")
        self._forecasts[forecast["forecast_id"]] = deepcopy(forecast)

    def put_decision(self, decision: dict[str, Any]) -> None:
        validate(decision, "epistemic_decision.schema.json")
        for claim_id in decision.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"decision references missing claim: {claim_id}")
        for fid in decision.get("depends_on_forecast_ids", []):
            if fid not in self._forecasts:
                raise EpistemicError(f"decision references missing forecast: {fid}")
        self._decisions[decision["decision_id"]] = deepcopy(decision)

    def put_commitment(self, commitment: dict[str, Any]) -> None:
        validate(commitment, "commitment.schema.json")
        for claim_id in commitment.get("depends_on_claim_ids", []):
            if claim_id not in self._claims:
                raise EpistemicError(f"commitment references missing claim: {claim_id}")
        self._commitments[commitment["commitment_id"]] = deepcopy(commitment)

    def put_assumption(self, assumption: dict[str, Any]) -> None:
        validate(assumption, "assumption.schema.json")
        self._assumptions[assumption["assumption_id"]] = deepcopy(assumption)

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
