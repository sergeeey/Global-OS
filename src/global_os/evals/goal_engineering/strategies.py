"""Tasking strategies under comparison.

S_TRAD            — traditional vague prompt ("do your best")
S_DETAIL          — detailed procedural steps (may be incomplete / brittle)
S_DETAIL_VERIFIED — complete runbook control (verify + retractions + test gate)
S_GE              — Goal Engineering: GoalContract + DoD + EvidenceLedger

Post-audit: S_DETAIL_VERIFIED is the fair procedural control for GE contrasts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

StrategyId = Literal["S_TRAD", "S_DETAIL", "S_DETAIL_VERIFIED", "S_GE"]

# v1 arms (immutable seal) excluded S_DETAIL_VERIFIED
STRATEGY_IDS_V1: tuple[StrategyId, ...] = ("S_TRAD", "S_DETAIL", "S_GE")
STRATEGY_IDS: tuple[StrategyId, ...] = (
    "S_TRAD",
    "S_DETAIL",
    "S_DETAIL_VERIFIED",
    "S_GE",
)


@dataclass(frozen=True)
class TaskingPacket:
    """What the agent receives before acting — the independent variable."""

    strategy_id: StrategyId
    task_id: str
    prompt_text: str
    goal_contract: dict[str, Any] = field(default_factory=dict)
    definition_of_done: list[dict[str, str]] = field(default_factory=list)
    evidence_requirements: list[dict[str, str]] = field(default_factory=list)
    procedural_steps: list[str] = field(default_factory=list)


def build_trad(task_id: str, objective: str) -> TaskingPacket:
    return TaskingPacket(
        strategy_id="S_TRAD",
        task_id=task_id,
        prompt_text=(
            f"Please solve the following task as best you can.\n\n"
            f"Task: {objective}\n\n"
            f"When you believe you are done, report SUCCESS and summarize what you did."
        ),
    )


def build_detail(task_id: str, objective: str, steps: list[str]) -> TaskingPacket:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return TaskingPacket(
        strategy_id="S_DETAIL",
        task_id=task_id,
        prompt_text=(
            f"Follow these instructions exactly to complete the task.\n\n"
            f"Objective: {objective}\n\n"
            f"Steps:\n{numbered}\n\n"
            f"After completing all steps in order, report SUCCESS."
        ),
        procedural_steps=list(steps),
    )


def build_detail_verified(
    task_id: str, objective: str, steps: list[str]
) -> TaskingPacket:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return TaskingPacket(
        strategy_id="S_DETAIL_VERIFIED",
        task_id=task_id,
        prompt_text=(
            f"Follow these verified runbook instructions exactly.\n\n"
            f"Objective: {objective}\n\n"
            f"Steps:\n{numbered}\n\n"
            f"Report SUCCESS only when every verification step has passed. "
            f"If a check fails, report BLOCKED — do not assert completion."
        ),
        procedural_steps=list(steps),
    )


def build_ge(
    task_id: str,
    objective: str,
    dod: list[dict[str, str]],
    evidence_reqs: list[dict[str, str]],
    *,
    non_goals: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> TaskingPacket:
    contract = {
        "goal_id": f"goal_{task_id}",
        "version": 1,
        "objective": {"text": objective},
        "success_criteria": [
            {"id": c["id"], "description": c["description"]} for c in dod
        ],
        "non_goals": list(non_goals or []),
        "forbidden_outcomes": list(forbidden or []),
        "evidence_requirements": {
            e["criterion_id"]: {"verification_tier": int(e.get("tier", "2"))}
            for e in evidence_reqs
        },
    }
    dod_text = "\n".join(f"- [{c['id']}] {c['description']}" for c in dod)
    ev_text = "\n".join(
        f"- criterion {e['criterion_id']}: require {e['kind']} ({e.get('note', '')})"
        for e in evidence_reqs
    )
    return TaskingPacket(
        strategy_id="S_GE",
        task_id=task_id,
        prompt_text=(
            f"You are bound by an immutable GoalContract.\n\n"
            f"Objective: {objective}\n\n"
            f"Definition of Done (all must hold):\n{dod_text}\n\n"
            f"EvidenceLedger requirements:\n{ev_text}\n\n"
            f"Do not claim SUCCESS until every DoD criterion has a ledger entry "
            f"with direct, scope-matched evidence. If evidence is missing, continue "
            f"or report BLOCKED — never assert completion from confidence alone."
        ),
        goal_contract=contract,
        definition_of_done=list(dod),
        evidence_requirements=list(evidence_reqs),
    )
