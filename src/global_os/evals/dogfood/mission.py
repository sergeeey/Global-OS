"""Dogfooding mission — Global OS on Global OS; no autonomous T0/T1 merge."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from global_os.runtime.events.ledger import EventLedger


class DogfoodStage(str, Enum):
    OBSERVE = "observe"
    ANALYZE = "analyze"
    PROPOSE = "propose"
    IMPLEMENT_BRANCH = "implement_branch"
    TEST = "test"
    VERIFY = "verify"
    REQUEST_MERGE = "request_merge"
    # Explicit non-stage: autonomous merge forbidden
    # MERGE_AUTONOMOUS = forbidden


STAGES_ORDER: tuple[DogfoodStage, ...] = (
    DogfoodStage.OBSERVE,
    DogfoodStage.ANALYZE,
    DogfoodStage.PROPOSE,
    DogfoodStage.IMPLEMENT_BRANCH,
    DogfoodStage.TEST,
    DogfoodStage.VERIFY,
    DogfoodStage.REQUEST_MERGE,
)


@dataclass
class DogfoodProposal:
    proposal_id: str
    title: str
    rationale: str
    priority: str
    touches_trusted_core: bool
    branch_name: str | None = None
    stage: DogfoodStage = DogfoodStage.OBSERVE
    autonomous_merge_allowed: bool = False
    history: list[dict[str, str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value
        return d


class DogfoodError(Exception):
    pass


class DogfoodMission:
    """Standing mission: improve Global OS via gated propose→branch→request merge."""

    MISSION = (
        "Watch Global OS repository, CI, tests, architecture claims and technical debt. "
        "Propose highest-value next improvement. Create implementation branches after "
        "priority confirmation. Production/trusted-core changes must not self-merge."
    )

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._proposals: dict[str, DogfoodProposal] = {}

    def propose(
        self,
        *,
        proposal_id: str,
        title: str,
        rationale: str,
        priority: str,
        touches_trusted_core: bool,
        tenant_id: str = "t",
        workspace_id: str = "w",
    ) -> dict[str, Any]:
        prop = DogfoodProposal(
            proposal_id=proposal_id,
            title=title,
            rationale=rationale,
            priority=priority,
            touches_trusted_core=touches_trusted_core,
            stage=DogfoodStage.PROPOSE,
            autonomous_merge_allowed=False,
            history=[{"stage": DogfoodStage.PROPOSE.value, "at": datetime.now(UTC).isoformat()}],
        )
        self._proposals[proposal_id] = prop
        self._ledger.append(
            event_type="dogfood.proposal_recorded",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            payload={
                "proposal_id": proposal_id,
                "title": title,
                "touches_trusted_core": touches_trusted_core,
                "autonomous_merge_allowed": False,
            },
            producer="evals.dogfood",
        )
        return prop.as_dict()

    def advance(
        self,
        proposal_id: str,
        next_stage: DogfoodStage,
        *,
        branch_name: str | None = None,
    ) -> dict[str, Any]:
        prop = self._proposals[proposal_id]
        cur_idx = STAGES_ORDER.index(prop.stage)
        next_idx = STAGES_ORDER.index(next_stage)
        if next_idx != cur_idx + 1:
            raise DogfoodError(
                f"stages must advance in order: {prop.stage.value} → {next_stage.value}"
            )
        if next_stage == DogfoodStage.IMPLEMENT_BRANCH and not branch_name:
            raise DogfoodError("branch_name required for implement_branch")
        if next_stage == DogfoodStage.REQUEST_MERGE and prop.touches_trusted_core:
            # Still allowed to *request* merge; autonomous merge remains forbidden
            pass
        prop.stage = next_stage
        if branch_name:
            prop.branch_name = branch_name
        prop.history.append(
            {"stage": next_stage.value, "at": datetime.now(UTC).isoformat()}
        )
        return prop.as_dict()

    def attempt_autonomous_merge(self, proposal_id: str) -> None:
        """Always fail closed — trusted or not, dogfood never self-merges."""
        prop = self._proposals.get(proposal_id)
        raise DogfoodError(
            "autonomous merge forbidden for dogfooding mission "
            f"(proposal={proposal_id}, trusted_core={getattr(prop, 'touches_trusted_core', None)})"
        )

    def list_proposals(self) -> list[dict[str, Any]]:
        return [deepcopy(p.as_dict()) for p in self._proposals.values()]
