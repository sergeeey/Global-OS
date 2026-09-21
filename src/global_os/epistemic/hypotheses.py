"""Hypothesis lifecycle (Y-17) — PROPOSED→ACTIVE→SUPPORTED|KILLED|INCONCLUSIVE→CLOSED."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from global_os.common.hashing import new_id
from global_os.runtime.events.ledger import EventLedger


class HypothesisState(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    KILLED = "KILLED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CLOSED = "CLOSED"


@dataclass
class Hypothesis:
    hypothesis_id: str
    goal_id: str
    statement: str
    state: HypothesisState
    kill_criteria: list[str]
    alternative_explanations: list[str]
    reopen_conditions: list[str]
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "goal_id": self.goal_id,
            "statement": self.statement,
            "state": self.state.value,
            "kill_criteria": list(self.kill_criteria),
            "alternative_explanations": list(self.alternative_explanations),
            "reopen_conditions": list(self.reopen_conditions),
            "evidence_ids": list(self.evidence_ids),
        }


class HypothesisError(Exception):
    pass


class HypothesisStore:
    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._items: dict[str, Hypothesis] = {}

    def propose(
        self,
        *,
        goal_id: str,
        statement: str,
        kill_criteria: list[str],
        alternative_explanations: list[str],
        reopen_conditions: list[str],
        tenant_id: str,
        workspace_id: str,
    ) -> Hypothesis:
        if not kill_criteria or not reopen_conditions:
            raise HypothesisError("kill_criteria and reopen_conditions required")
        h = Hypothesis(
            hypothesis_id=new_id("hyp"),
            goal_id=goal_id,
            statement=statement,
            state=HypothesisState.PROPOSED,
            kill_criteria=kill_criteria,
            alternative_explanations=alternative_explanations,
            reopen_conditions=reopen_conditions,
        )
        self._items[h.hypothesis_id] = h
        self._emit(h, tenant_id, workspace_id, "proposed")
        return deepcopy(h)

    def activate(self, hypothesis_id: str, *, tenant_id: str, workspace_id: str) -> Hypothesis:
        h = self._items[hypothesis_id]
        if h.state != HypothesisState.PROPOSED:
            raise HypothesisError("only PROPOSED can become ACTIVE")
        h.state = HypothesisState.ACTIVE
        self._emit(h, tenant_id, workspace_id, "activated")
        return deepcopy(h)

    def resolve(
        self,
        hypothesis_id: str,
        outcome: HypothesisState,
        *,
        tenant_id: str,
        workspace_id: str,
        null_result: bool = False,
    ) -> Hypothesis:
        h = self._items[hypothesis_id]
        if h.state != HypothesisState.ACTIVE:
            raise HypothesisError("only ACTIVE can resolve")
        if outcome not in {
            HypothesisState.SUPPORTED,
            HypothesisState.KILLED,
            HypothesisState.INCONCLUSIVE,
        }:
            raise HypothesisError("invalid resolve outcome")
        h.state = outcome
        self._emit(h, tenant_id, workspace_id, "resolved", extra={"null_result": null_result})
        if null_result or outcome == HypothesisState.KILLED:
            self._ledger.append(
                event_type="null_result.recorded",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                goal_id=h.goal_id,
                payload={
                    "hypothesis_id": h.hypothesis_id,
                    "attempt": h.statement,
                    "why_failed": f"resolved as {outcome.value}",
                    "reopen_condition": h.reopen_conditions[0],
                },
                producer="epistemic.hypotheses",
            )
        return deepcopy(h)

    def close(self, hypothesis_id: str, *, tenant_id: str, workspace_id: str) -> Hypothesis:
        h = self._items[hypothesis_id]
        if h.state not in {
            HypothesisState.SUPPORTED,
            HypothesisState.KILLED,
            HypothesisState.INCONCLUSIVE,
        }:
            raise HypothesisError("close only after resolve")
        h.state = HypothesisState.CLOSED
        self._emit(h, tenant_id, workspace_id, "closed")
        return deepcopy(h)

    def get(self, hypothesis_id: str) -> Hypothesis:
        return deepcopy(self._items[hypothesis_id])

    def _emit(
        self,
        h: Hypothesis,
        tenant_id: str,
        workspace_id: str,
        action: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        payload = h.to_dict()
        payload["action"] = action
        if extra:
            payload.update(extra)
        # reuse claim.staled-like channel via task.transitioned for lifecycle breadcrumbs
        self._ledger.append(
            event_type="task.transitioned",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=h.goal_id,
            payload=payload,
            producer="epistemic.hypotheses",
        )
