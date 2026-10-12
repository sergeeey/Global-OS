"""Strategic Goal Decomposer stub — plan only; no world effects."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.common.hashing import content_hash, new_id


class DecomposerError(Exception):
    pass


def decompose_goal(goal: dict[str, Any], *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a phased strategy plan bound to the Goal Contract hash.

    Control transfer: returns plan for Orchestration — never ActionProposals.
    """
    del context  # reserved
    required = ("goal_id", "version", "objective", "success_criteria", "invariants")
    missing = [k for k in required if k not in goal]
    if missing:
        raise DecomposerError(f"CLARIFICATION_REQUIRED: missing {missing}")

    goal_hash = goal.get("content_hash") or content_hash(
        {k: v for k, v in goal.items() if k != "content_hash"}
    )
    criteria = goal["success_criteria"]
    if not criteria:
        raise DecomposerError("CLARIFICATION_REQUIRED: empty success_criteria")

    criterion_ids = [
        c if isinstance(c, str) else str(c.get("id") or c.get("description") or c)
        for c in criteria
    ]
    phases = [
        {
            "phase_id": "phase_audit",
            "intent": "discover defects against goal criteria",
            "exit_criteria": [c if isinstance(c, str) else c.get("description", str(c)) for c in criteria],
            "advances_criteria": list(criterion_ids),
        },
        {
            "phase_id": "phase_fix",
            "intent": "apply bounded fixes under invariants",
            "exit_criteria": list(goal.get("invariants") or []),
            "advances_criteria": list(criterion_ids),
        },
        {
            "phase_id": "phase_accept",
            "intent": "accept against Goal success_criteria",
            "exit_criteria": [c if isinstance(c, str) else c.get("description", str(c)) for c in criteria],
            "advances_criteria": list(criterion_ids),
        },
    ]
    tasks = build_repo_audit_dag(str(goal["goal_id"]))
    # Q-D6: plan-level map (task schema additionalProperties:false — no silent field inject)
    task_advances = {t["task_id"]: list(criterion_ids) for t in tasks}
    if any(not refs for refs in task_advances.values()):
        raise DecomposerError("PLAN_REJECTED: task with empty advances_criteria (Q-D6)")
    body = {
        "plan_id": new_id("plan"),
        "goal_id": goal["goal_id"],
        "goal_version": goal["version"],
        "goal_content_hash": goal_hash,
        "phases": phases,
        "tasks": tasks,
        "task_advances_criteria": task_advances,
        "omitted_alternatives": [],
        "selection": {
            "mechanism": "goal_progress",
            "rule": "every_task_maps_to_success_criteria",
        },
        "priority_scores": {"default": "risk_x_value_stub"},
        "handoff_to": "orchestration",
        "world_effects": False,
    }
    body["content_hash"] = content_hash(body)
    return deepcopy(body)


def refuse_goal_overwrite(goal: dict[str, Any], mutated: dict[str, Any]) -> None:
    """Control rule: Decomposer must not silently mutate Goal."""
    g_hash = goal.get("content_hash")
    m_hash = mutated.get("content_hash")
    if g_hash and m_hash and g_hash != m_hash:
        raise DecomposerError("silent goal mutation forbidden (GOS-I06/I27)")
    if goal.get("objective") != mutated.get("objective"):
        raise DecomposerError("silent goal mutation forbidden (GOS-I06/I27)")
