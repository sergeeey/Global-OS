"""Contextual Task Compiler — deterministic Execution Brief (T2, ADR-0009).

Composes Goal + plan task + EnvironmentCompiler into a structured work order.
Does not call models. Does not mutate Goal. Does not certify completion.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.cognition.environment import EnvironmentCompiler, EnvironmentCompilerError
from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate

MATERIAL_REASONS = frozenset(
    {
        "first_attempt",
        "pivot",
        "partial_unknown",
        "operator_resume",
        "blocker",
        "executor_change",
    }
)


class TaskCompilerError(Exception):
    pass


def _goal_criterion_ids(goal: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            out.append(c)
        else:
            cid = str(c.get("id") or "")
            if cid:
                out.append(cid)
    return out


def _goal_objective_text(goal: dict[str, Any]) -> str:
    obj = goal.get("objective")
    if isinstance(obj, dict):
        return str(obj.get("text") or obj)
    return str(obj or "")


def _default_org_unit(goal: dict[str, Any], *, budget: dict[str, Any] | None = None) -> dict[str, Any]:
    caps = list(goal.get("authority", {}).get("capabilities") or [])
    b = budget or {"usd": 0.0, "tokens": 0}
    return {
        "id": "org_ctc_default",
        "authority": {"capabilities": caps},
        "budget": {
            "usd": float(b.get("usd", 0) or 0),
            "tokens": int(b.get("tokens", 0) or 0),
        },
        "output_contract": "artifact_and_evidence",
    }


def resolve_brief_criterion_ids(
    *,
    goal: dict[str, Any],
    plan: dict[str, Any],
    task: dict[str, Any],
    explicit: list[str] | None = None,
) -> list[str]:
    """Select criteria for this brief — never silently bind every Goal criterion.

    Prefer explicit ids. Else plan task_advances for this task, but if that set
    equals the full Goal criteria set (underspecified decomposer map), bind none
    so Completion Gate leaves them UNKNOWN until a scoped verifier binds them.
    """
    goal_ids = _goal_criterion_ids(goal)
    goal_set = set(goal_ids)
    if explicit is not None:
        chosen = [c for c in explicit if c in goal_set]
        unknown = set(explicit) - goal_set
        if unknown:
            raise TaskCompilerError(f"criterion_ids not in Goal: {sorted(unknown)}")
        return chosen

    task_id = str(task.get("task_id") or "")
    advances_map = plan.get("task_advances_criteria") or {}
    raw = list(advances_map.get(task_id) or [])
    chosen = [c for c in raw if c in goal_set]
    if chosen and set(chosen) == goal_set and len(goal_set) > 1:
        return []
    return chosen


def should_emit_new_brief(
    *,
    material_reason: str,
    prior_brief: dict[str, Any] | None,
    prior_failure_class: str | None = None,
    new_failure_class: str | None = None,
) -> bool:
    """Material-change gate — avoid brief-spam on every micro-op."""
    if material_reason not in MATERIAL_REASONS:
        raise TaskCompilerError(f"unsupported material_reason: {material_reason}")
    if prior_brief is None:
        return True
    if material_reason in {"first_attempt", "pivot", "operator_resume", "blocker", "executor_change"}:
        return True
    if material_reason == "partial_unknown":
        return prior_failure_class != new_failure_class
    return False


def compile_execution_brief(
    *,
    goal: dict[str, Any],
    plan: dict[str, Any],
    task: dict[str, Any],
    org_unit: dict[str, Any] | None = None,
    ledger_tail: list[dict[str, Any]] | None = None,
    material_reason: str = "first_attempt",
    criterion_ids: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    prior_brief: dict[str, Any] | None = None,
    prior_failure_class: str | None = None,
    new_failure_class: str | None = None,
    force: bool = False,
) -> dict[str, Any] | None:
    """Compile a structured Execution Brief (deterministic; no model calls).

    Returns None when material-change gate says a new brief is not required
    (unless ``force``). Never mutates ``goal``.
    """
    if material_reason not in MATERIAL_REASONS:
        raise TaskCompilerError(f"unsupported material_reason: {material_reason}")
    if not force and not should_emit_new_brief(
        material_reason=material_reason,
        prior_brief=prior_brief,
        prior_failure_class=prior_failure_class,
        new_failure_class=new_failure_class,
    ):
        return None

    goal_snapshot = deepcopy(goal)
    org = org_unit or _default_org_unit(goal_snapshot)
    goal_caps = set(goal_snapshot.get("authority", {}).get("capabilities") or [])
    org_caps = set(org.get("authority", {}).get("capabilities") or [])
    if not org_caps.issubset(goal_caps):
        raise TaskCompilerError("org capabilities must be ⊆ goal (GOS-I04)")

    if "task_id" not in task:
        raise TaskCompilerError("task.task_id required")

    try:
        env = EnvironmentCompiler().compile(
            goal=goal_snapshot,
            org_unit=org,
            task=task,
            verification_tier=int(
                (goal_snapshot.get("evidence_requirements") or {})
                .get("major_finding", {})
                .get("verification_tier", 1)
            ),
        )
    except EnvironmentCompilerError as exc:
        raise TaskCompilerError(str(exc)) from exc

    allowed = list(env.get("tools", {}).get("allow") or [])
    if not set(allowed).issubset(goal_caps):
        raise TaskCompilerError("allowed_tools must be ⊆ goal capabilities")

    bound_criteria = resolve_brief_criterion_ids(
        goal=goal_snapshot, plan=plan, task=task, explicit=criterion_ids
    )

    rb = env.get("reasoning_budget", {}).get("requested") or {}
    budget = {
        "usd": float(rb.get("usd", 0) or 0),
        "tokens": int(rb.get("tokens", 0) or 0),
    }

    constraints = [str(x) for x in (goal_snapshot.get("invariants") or [])]
    constraints.append("no_goal_mutation")
    constraints.append("no_self_certification")

    risk = goal_snapshot.get("risk") or {}
    human_approval = str(risk.get("maximum_irreversibility") or "none") not in {
        "none",
        "",
    }

    context_refs = ["goal_contract", str(task["task_id"]), str(plan.get("plan_id") or "")]
    context_refs = [r for r in context_refs if r]
    for ev in (ledger_tail or [])[-5:]:
        eid = ev.get("event_id")
        if eid:
            context_refs.append(str(eid))

    obj = _goal_objective_text(goal_snapshot)
    title = str(task.get("title") or task["task_id"])
    if bound_criteria:
        crit_clause = ", ".join(bound_criteria)
        objective_text = (
            f"Advance Goal {goal_snapshot.get('goal_id')} via task '{title}': "
            f"produce evidence for criteria [{crit_clause}]. "
            f"Outcome context: {obj[:240]}"
        )
    else:
        objective_text = (
            f"Advance Goal {goal_snapshot.get('goal_id')} via task '{title}' "
            f"without claiming unverified criteria. Clarify scoped evidence needs. "
            f"Outcome context: {obj[:240]}"
        )

    artifacts = list(
        expected_artifacts
        or ["effect_receipt", "artifact_digest"]
    )

    brief: dict[str, Any] = {
        "brief_id": new_id("brf"),
        "schema_version": "0.1.0",
        "goal_id": str(goal_snapshot["goal_id"]),
        "goal_version": int(goal_snapshot.get("version") or 1),
        "plan_id": str(plan.get("plan_id") or "plan_unknown"),
        "task_id": str(task["task_id"]),
        "objective_text": objective_text,
        "criterion_ids": bound_criteria,
        "allowed_tools": allowed,
        "budget": budget,
        "expected_artifacts": artifacts,
        "verification_method": "effect_receipt_completion_gate",
        "constraints": constraints,
        "human_approval_required": human_approval,
        "context_refs": context_refs,
        "authority_check": {"caps_subset": True},
        "material_reason": material_reason,
        "env_id": str(env["id"]),
        "org_unit_id": str(org.get("id") or env.get("org_unit_id")),
    }
    brief["content_hash"] = content_hash(
        {k: v for k, v in brief.items() if k not in {"brief_id", "content_hash"}}
    )
    validate(brief, "execution_brief.schema.json")
    # Goal is only read via deepcopy — never written.
    del goal_snapshot
    return brief
