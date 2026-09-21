"""Clarification policy — ask vs assume; assumptions always recorded in Epistemic Kernel."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from global_os.cognition.metareasoning.materiality import MaterialityLevel, assess_materiality
from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.epistemic.store import EpistemicStore
from global_os.runtime.events.ledger import EventLedger


class ClarificationEngine:
    def __init__(
        self,
        ledger: EventLedger,
        epistemic: EpistemicStore | None = None,
    ) -> None:
        self._ledger = ledger
        self._epistemic = epistemic
        self._assumptions: dict[str, dict[str, Any]] = {}

    def decide(
        self,
        policy: dict[str, Any],
        *,
        situation: str,
        impact: str,
        probability: float,
        irreversibility: str,
        goal_sensitivity: float,
        goal_id: str,
        tenant_id: str,
        workspace_id: str,
        assumption_statement: str,
        task_id: str | None = None,
        depends_on_claim_ids: list[str] | None = None,
        depends_on_evidence_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        validate(policy, "clarification_policy.schema.json")
        mat = assess_materiality(
            impact=impact,
            probability=probability,
            irreversibility=irreversibility,
            goal_sensitivity=goal_sensitivity,
        )
        ask_when = set(policy.get("ask_when", []))
        assume_when = set(policy.get("assume_when", []))

        must_ask = situation in ask_when or (
            policy.get("materiality_policy") == "materiality_based" and mat.ask_human
        )
        may_assume = situation in assume_when and mat.level in {
            MaterialityLevel.NONE,
            MaterialityLevel.LOW,
        }

        if must_ask and not may_assume:
            return {"action": "ask", "materiality": mat.level.value, "rationale": mat.rationale}

        if policy.get("record_assumption", True):
            assumption_id: str = new_id("asm")
            assumption: dict[str, Any] = {
                "assumption_id": assumption_id,
                "schema_version": "0.1.0",
                "goal_id": goal_id,
                "task_id": task_id,
                "statement": assumption_statement,
                "status": "ACTIVE",
                "origin": "clarification_skipped",
                "materiality": mat.level.value,
                "ask_deferred": True,
                "recorded_at": datetime.now(UTC).isoformat(),
                "reopen_condition": "materiality increased or user dispute",
            }
            if depends_on_claim_ids:
                assumption["depends_on_claim_ids"] = list(depends_on_claim_ids)
            if depends_on_evidence_ids:
                assumption["depends_on_evidence_ids"] = list(depends_on_evidence_ids)
            assumption = {k: v for k, v in assumption.items() if v is not None}
            validate(assumption, "assumption.schema.json")
            self._assumptions[assumption_id] = assumption
            if self._epistemic is not None:
                self._epistemic.put_assumption(assumption)
            self._ledger.append(
                event_type="task.transitioned",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                goal_id=goal_id,
                task_id=task_id,
                payload={"kind": "assumption_recorded", **assumption},
                producer="cognition.clarification",
            )
            return {
                "action": "assume",
                "assumption": assumption,
                "materiality": mat.level.value,
                "rationale": mat.rationale,
            }

        return {"action": "assume", "materiality": mat.level.value, "rationale": mat.rationale}

    def get_assumption(self, assumption_id: str) -> dict[str, Any]:
        if self._epistemic is not None:
            return self._epistemic.get_assumption(assumption_id)
        return dict(self._assumptions[assumption_id])
