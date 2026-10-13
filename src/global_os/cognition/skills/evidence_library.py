"""Evidence-backed skill library — progressive disclosure + transfer evidence.

SKILL.md-style metadata is not enough: provenance, applicability, eval status,
required capabilities, and negative evidence are first-class.
Promotion never automatic (EXPERIMENTAL until human).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

ALLOWED_STATUSES = frozenset(
    {"EXPERIMENTAL", "TRANSFER_PENDING", "REJECTED", "PROMOTED_BY_HUMAN", "DEPRECATED"}
)


@dataclass
class SkillEvidence:
    suite_id: str
    success_rate: float
    n_trials: int
    cost_tokens: float
    disjoint_from_train: bool
    recorded_at_utc: str
    notes: str = ""


@dataclass
class EvidenceSkill:
    skill_id: str
    title: str
    instructions: str
    applies_to_task_types: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    provenance: dict[str, Any]
    status: str = "EXPERIMENTAL"
    positive_evidence: list[SkillEvidence] = field(default_factory=list)
    negative_evidence: list[SkillEvidence] = field(default_factory=list)
    better_than: str | None = None
    stale_after_utc: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "title": self.title,
            "instructions": self.instructions,
            "applies_to_task_types": list(self.applies_to_task_types),
            "required_capabilities": list(self.required_capabilities),
            "provenance": dict(self.provenance),
            "status": self.status,
            "positive_evidence": [
                {
                    "suite_id": e.suite_id,
                    "success_rate": e.success_rate,
                    "n_trials": e.n_trials,
                    "cost_tokens": e.cost_tokens,
                    "disjoint_from_train": e.disjoint_from_train,
                    "recorded_at_utc": e.recorded_at_utc,
                    "notes": e.notes,
                }
                for e in self.positive_evidence
            ],
            "negative_evidence": [
                {
                    "suite_id": e.suite_id,
                    "success_rate": e.success_rate,
                    "n_trials": e.n_trials,
                    "cost_tokens": e.cost_tokens,
                    "disjoint_from_train": e.disjoint_from_train,
                    "recorded_at_utc": e.recorded_at_utc,
                    "notes": e.notes,
                }
                for e in self.negative_evidence
            ],
            "better_than": self.better_than,
            "stale_after_utc": self.stale_after_utc,
        }


class EvidenceSkillLibrary:
    """Process-local library; human promotion only."""

    def __init__(self) -> None:
        self._skills: dict[str, EvidenceSkill] = {}

    def register(self, skill: EvidenceSkill) -> EvidenceSkill:
        if skill.status not in ALLOWED_STATUSES:
            raise ValueError(f"illegal skill status: {skill.status}")
        if skill.status == "PROMOTED_BY_HUMAN":
            raise ValueError("register() cannot self-promote; use promote_by_human")
        # New skills start experimental
        skill.status = "EXPERIMENTAL"
        self._skills[skill.skill_id] = skill
        return skill

    def record_eval(
        self,
        skill_id: str,
        *,
        suite_id: str,
        success_rate: float,
        n_trials: int,
        cost_tokens: float,
        disjoint_from_train: bool,
        positive: bool,
        notes: str = "",
    ) -> EvidenceSkill:
        skill = self._skills[skill_id]
        # Refuse tiny universal admission claims (7/10 not enough to auto-promote)
        ev = SkillEvidence(
            suite_id=suite_id,
            success_rate=success_rate,
            n_trials=n_trials,
            cost_tokens=cost_tokens,
            disjoint_from_train=disjoint_from_train,
            recorded_at_utc=datetime.now(UTC).isoformat(),
            notes=notes,
        )
        if positive:
            skill.positive_evidence.append(ev)
            if disjoint_from_train:
                skill.status = "TRANSFER_PENDING"
        else:
            skill.negative_evidence.append(ev)
            if success_rate < 0.5 and n_trials >= 3:
                skill.status = "REJECTED"
        return skill

    def promote_by_human(self, skill_id: str, *, approver: str) -> EvidenceSkill:
        skill = self._skills[skill_id]
        if not skill.positive_evidence:
            raise ValueError("cannot promote without positive evidence")
        transfer_ok = any(e.disjoint_from_train for e in skill.positive_evidence)
        if not transfer_ok:
            raise ValueError("cannot promote without disjoint transfer evidence")
        # Explicitly reject 7/10-only admission
        best = max(skill.positive_evidence, key=lambda e: (e.disjoint_from_train, e.n_trials))
        if best.n_trials < 20 and best.success_rate < 0.9:
            raise ValueError(
                "admission sample too small/uncertain for promotion "
                f"(n={best.n_trials}, rate={best.success_rate})"
            )
        skill.status = "PROMOTED_BY_HUMAN"
        skill.provenance = {
            **skill.provenance,
            "promoted_by": approver,
            "promoted_at_utc": datetime.now(UTC).isoformat(),
        }
        return skill

    def select_for_task(
        self, task_type: str, *, allow_experimental: bool = False
    ) -> list[EvidenceSkill]:
        out: list[EvidenceSkill] = []
        for skill in self._skills.values():
            if task_type not in skill.applies_to_task_types:
                continue
            if skill.status == "REJECTED" or skill.status == "DEPRECATED":
                continue
            if skill.status == "EXPERIMENTAL" and not allow_experimental:
                continue
            out.append(skill)
        # Prefer promoted, then transfer-pending with higher success
        def key(s: EvidenceSkill) -> tuple[int, float]:
            rank = 2 if s.status == "PROMOTED_BY_HUMAN" else 1 if s.status == "TRANSFER_PENDING" else 0
            rate = max((e.success_rate for e in s.positive_evidence), default=0.0)
            return (rank, rate)

        return sorted(out, key=key, reverse=True)

    def as_dicts(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._skills.values()]
