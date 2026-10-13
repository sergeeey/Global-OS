"""Contrastive Failure Miner v0 — analyze-only (no runtime mutation)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContrastiveFinding:
    failure_class: str
    module_hint: str
    detail: str
    support_count: int
    success_contrast: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_class": self.failure_class,
            "module_hint": self.module_hint,
            "detail": self.detail,
            "support_count": self.support_count,
            "success_contrast": self.success_contrast,
            "mutates_runtime": False,
        }


def _terminal(traj: dict[str, Any]) -> str:
    return str(
        (traj.get("verified_outcome") or {}).get("terminal")
        or traj.get("terminal")
        or "UNKNOWN"
    )


def _tools(traj: dict[str, Any]) -> list[str]:
    steps = traj.get("steps") or traj.get("actions") or []
    out: list[str] = []
    for s in steps:
        if isinstance(s, dict):
            t = s.get("tool") or s.get("tool_id") or s.get("chosen_tool")
            if t:
                out.append(str(t))
    return out


def mine_contrastive_failures(
    trajectories: list[dict[str, Any]],
    *,
    goal_id: str | None = None,
) -> dict[str, Any]:
    """Compare success vs failure runs of the same goal; propose failure_classes only."""
    if len(trajectories) < 2:
        raise ValueError("contrastive miner requires ≥2 trajectories")

    filtered = [
        t
        for t in trajectories
        if goal_id is None or str((t.get("goal") or {}).get("goal_id") or t.get("goal_id")) == goal_id
    ]
    if len(filtered) < 2:
        filtered = trajectories

    successes = [t for t in filtered if _terminal(t) in {"SUCCESS", "ACHIEVED"}]
    failures = [
        t
        for t in filtered
        if _terminal(t) in {"FAILED", "PARTIAL", "STOPPED", "UNKNOWN"}
    ]
    if not successes or not failures:
        return {
            "findings": [],
            "proposals": [],
            "mutates_runtime": False,
            "reason": "need_both_success_and_failure_trajectories",
            "n_success": len(successes),
            "n_failure": len(failures),
        }

    # Tool choice contrast
    success_tools = Counter(t for s in successes for t in _tools(s))
    failure_tools = Counter(t for f in failures for t in _tools(f))
    findings: list[ContrastiveFinding] = []

    for tool, n in failure_tools.most_common():
        if success_tools.get(tool, 0) == 0 and n >= 1:
            findings.append(
                ContrastiveFinding(
                    failure_class="wrong_tool_selection",
                    module_hint="orchestration",
                    detail=f"failure runs used {tool!r} which success runs never used",
                    support_count=n,
                    success_contrast=f"success_tools={dict(success_tools)}",
                )
            )

    # Premature stop
    for f in failures:
        if f.get("premature_stop") or str(f.get("stop_reason") or "") in {
            "STOP_NO_STRATEGY",
            "budget",
            "gave_up",
        }:
            findings.append(
                ContrastiveFinding(
                    failure_class="premature_stop",
                    module_hint="pivot_replan",
                    detail=str(f.get("stop_reason") or "premature_stop"),
                    support_count=1,
                    success_contrast="success runs continued to verified terminal",
                )
            )

    # Context / handoff loss
    for f in failures:
        if f.get("context_loss") or f.get("dropped_requirement"):
            findings.append(
                ContrastiveFinding(
                    failure_class="context_loss",
                    module_hint="context_management",
                    detail=str(f.get("dropped_requirement") or "context_loss"),
                    support_count=1,
                    success_contrast="success retained critical requirement",
                )
            )

    # Explicit failure_class on trajectories
    for f in failures:
        for item in f.get("failures") or []:
            if isinstance(item, dict) and item.get("failure_class"):
                findings.append(
                    ContrastiveFinding(
                        failure_class=str(item["failure_class"]),
                        module_hint=str(item.get("module_hint") or "unknown"),
                        detail=str(item.get("detail") or ""),
                        support_count=1,
                        success_contrast="see success trajectories",
                    )
                )

    # Deduplicate by failure_class+detail
    uniq: dict[tuple[str, str], ContrastiveFinding] = {}
    for finding in findings:
        key = (finding.failure_class, finding.detail)
        if key not in uniq or finding.support_count > uniq[key].support_count:
            uniq[key] = finding

    ordered = sorted(uniq.values(), key=lambda x: (-x.support_count, x.failure_class))
    proposals = [
        {
            "proposal_kind": "improvement_candidate_stub",
            "failure_class": f.failure_class,
            "target_component": f.module_hint
            if f.module_hint
            in {
                "orchestration",
                "decomposer",
                "pivot_replan",
                "workflow_unprivileged",
                "memory_handoff",
                "tool_selection_policy",
            }
            else "workflow_unprivileged",
            "mutates_runtime": False,
            "next": "feed_mission_learning_loop_v0",
        }
        for f in ordered[:5]
    ]
    return {
        "findings": [f.to_dict() for f in ordered],
        "proposals": proposals,
        "mutates_runtime": False,
        "n_success": len(successes),
        "n_failure": len(failures),
        "reason": "contrastive_ok",
    }
