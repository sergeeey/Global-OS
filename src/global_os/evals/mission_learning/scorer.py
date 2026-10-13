"""Independent MLLv0 scorer — no LLM oracle; workflow policy → metrics."""

from __future__ import annotations

from typing import Any


def score_workflow_policy(
    *,
    policy: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> dict[str, float]:
    """Deterministic sandbox score for unprivileged tool-selection policies.

    Each task has ``correct_tool`` and optional ``distractors``.
    Policy maps ``task_type`` → preferred tool id.
    """
    if not tasks:
        return {"success_rate": 0.0, "cost_tokens": 0.0, "wrong_tool_calls": 0.0}

    wrong = 0
    tokens = 0.0
    success = 0
    mapping = dict(policy.get("tool_by_task_type") or {})
    default_tool = str(policy.get("default_tool") or "")

    for task in tasks:
        ttype = str(task.get("task_type") or "")
        correct = str(task.get("correct_tool") or "")
        chosen = str(mapping.get(ttype) or default_tool)
        # Base cost + penalty for wrong tool / retry simulation
        tokens += float(task.get("base_tokens") or 10)
        if chosen == correct and chosen:
            success += 1
        else:
            wrong += 1
            tokens += float(task.get("retry_tokens") or 40)

    n = len(tasks)
    return {
        "success_rate": success / n,
        "cost_tokens": tokens,
        "wrong_tool_calls": float(wrong),
    }


def better_than_parent(
    *,
    candidate_score: dict[str, float],
    parent_score: dict[str, float],
    minimum_improvement: float,
) -> bool:
    """Benefit = fewer wrong tools (primary) with success_rate not worse."""
    c_wrong = candidate_score.get("wrong_tool_calls", 0.0)
    p_wrong = parent_score.get("wrong_tool_calls", 0.0)
    c_sr = candidate_score.get("success_rate", 0.0)
    p_sr = parent_score.get("success_rate", 0.0)
    if c_sr + 1e-9 < p_sr:
        return False
    return (p_wrong - c_wrong) >= float(minimum_improvement)
