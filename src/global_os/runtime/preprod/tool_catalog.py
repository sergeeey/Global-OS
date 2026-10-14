"""Operator tool catalog — capability → registered Gateway tool IDs (Fork B Phase 1).

No ToolKernel. Fail-closed on unknown/forbidden tools. Read-only tools only.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from global_os.world.tools.repo_audit import run_repo_audit
from global_os.world.tools.repo_inventory import run_repo_inventory, verify_repo_inventory_report

ProduceFn = Callable[[Path, dict[str, Any]], dict[str, Any]]
VerifyFn = Callable[[Any], dict[str, Any]]


def verify_repo_audit_report(report: Any) -> dict[str, Any]:
    """Deterministic independent check of a repo-audit artifact."""
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("read_only") is not True:
        return {"ok": False, "reason": "read_only_not_true"}
    findings = report.get("findings")
    if not isinstance(findings, list) or len(findings) < 1:
        return {"ok": False, "reason": "empty_or_missing_findings"}
    if not isinstance(report.get("scan"), dict):
        return {"ok": False, "reason": "missing_scan"}
    return {
        "ok": True,
        "reason": "deterministic_structure_ok",
        "finding_count": len(findings),
    }


@dataclass(frozen=True)
class OperatorToolSpec:
    tool_id: str
    required_capabilities: tuple[str, ...]
    intended_effect: str
    artifact_kind: str
    desc_markers: tuple[str, ...]
    exclude_markers: tuple[str, ...] = ()


class ToolCatalogError(Exception):
    pass


def _produce_repo_audit(target: Path, hooks: dict[str, Any]) -> dict[str, Any]:
    if hooks.get("inject_corrupt_report"):
        return {"findings": [], "modified_target": True}
    if hooks.get("inject_empty_report"):
        return {"findings": [], "read_only": True, "modified_target": False, "scan": {}}
    return run_repo_audit(target)


def _produce_repo_inventory(target: Path, hooks: dict[str, Any]) -> dict[str, Any]:
    if hooks.get("inject_corrupt_report"):
        return {
            "kind": "repo_inventory",
            "entries": [],
            "modified_target": True,
            "read_only": True,
        }
    if hooks.get("inject_empty_report"):
        return {
            "kind": "repo_inventory",
            "entries": [],
            "read_only": True,
            "modified_target": False,
        }
    return run_repo_inventory(target)


# Specs without produce/verify callables (those resolved via TOOL_IMPL)
OPERATOR_TOOL_SPECS: dict[str, OperatorToolSpec] = {
    "repo.audit": OperatorToolSpec(
        tool_id="repo.audit",
        required_capabilities=("filesystem.read",),
        intended_effect="repo_audit_report",
        artifact_kind="repo_audit_report",
        desc_markers=(
            "engineering report",
            "audit report",
            "repo audit",
            "verified engineering report",
        ),
        exclude_markers=(
            "integration test",
            "интеграционн",
            "tests passed",
            "тесты прошли",
            "e2e passed",
            "pytest",
            "inventory",
            "file listing",
            "directory listing",
        ),
    ),
    "repo.inventory": OperatorToolSpec(
        tool_id="repo.inventory",
        required_capabilities=("filesystem.read",),
        intended_effect="repo_inventory_report",
        artifact_kind="repo_inventory",
        desc_markers=(
            "inventory",
            "file listing",
            "directory listing",
            "workspace inventory",
            "list top-level",
        ),
        exclude_markers=(
            "integration test",
            "интеграционн",
            "engineering report",
            "audit report",
        ),
    ),
}


TOOL_IMPL: dict[str, tuple[ProduceFn, VerifyFn]] = {
    "repo.audit": (_produce_repo_audit, verify_repo_audit_report),
    "repo.inventory": (_produce_repo_inventory, verify_repo_inventory_report),
}


def registered_tool_ids() -> frozenset[str]:
    return frozenset(OPERATOR_TOOL_SPECS)


def capability_to_tool_ids() -> dict[str, list[str]]:
    """Inverse index: capability → tool ids that require it."""
    out: dict[str, list[str]] = {}
    for tid, spec in OPERATOR_TOOL_SPECS.items():
        for cap in spec.required_capabilities:
            out.setdefault(cap, []).append(tid)
    return out


def resolve_allowed_tool_ids(
    *,
    goal_capabilities: list[str] | set[str],
    brief_allowed_capabilities: list[str] | set[str],
) -> list[str]:
    """Tools whose required capabilities ⊆ goal ∩ brief allow-lists.

    Fail-closed: unknown capabilities in brief do not invent tools.
    """
    goal_caps = set(goal_capabilities)
    brief_caps = set(brief_allowed_capabilities)
    allowed_caps = goal_caps & brief_caps
    out: list[str] = []
    for tid, spec in sorted(OPERATOR_TOOL_SPECS.items()):
        req = set(spec.required_capabilities)
        if not req:
            continue
        if req.issubset(allowed_caps):
            out.append(tid)
    return out


def assert_tool_permitted(
    tool_id: str,
    *,
    allowed_tool_ids: list[str] | set[str],
) -> OperatorToolSpec:
    if tool_id not in OPERATOR_TOOL_SPECS:
        raise ToolCatalogError(f"unknown_tool_id:{tool_id}")
    if tool_id not in set(allowed_tool_ids):
        raise ToolCatalogError(f"forbidden_tool_id:{tool_id}")
    return OPERATOR_TOOL_SPECS[tool_id]


def criteria_supported_by_tool(goal: dict[str, Any], tool_id: str) -> list[str]:
    if tool_id not in OPERATOR_TOOL_SPECS:
        return []
    spec = OPERATOR_TOOL_SPECS[tool_id]
    supported: list[str] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            cid, desc = c, c
        else:
            cid = str(c.get("id") or "")
            desc = str(c.get("description") or "")
        if not cid:
            continue
        lowered = desc.lower()
        if any(m in lowered for m in spec.exclude_markers):
            continue
        if any(m in lowered for m in spec.desc_markers):
            supported.append(cid)
    return supported


def criteria_supported_by_tools(goal: dict[str, Any], tool_ids: list[str]) -> list[str]:
    seen: list[str] = []
    for tid in tool_ids:
        for cid in criteria_supported_by_tool(goal, tid):
            if cid not in seen:
                seen.append(cid)
    return seen


def produce_tool_artifact(
    tool_id: str, target: Path, hooks: dict[str, Any]
) -> dict[str, Any]:
    if tool_id not in TOOL_IMPL:
        raise ToolCatalogError(f"unknown_tool_id:{tool_id}")
    produce, _verify = TOOL_IMPL[tool_id]
    return produce(target, hooks)


def verify_tool_artifact(tool_id: str, report: Any) -> dict[str, Any]:
    if tool_id not in TOOL_IMPL:
        return {"ok": False, "reason": f"unknown_tool_id:{tool_id}"}
    _produce, verify = TOOL_IMPL[tool_id]
    return verify(report)
