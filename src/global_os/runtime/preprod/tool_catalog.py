"""Operator tool catalog — capability → registered Gateway tool IDs.

No ToolKernel. Fail-closed on unknown/forbidden tools / invalid args.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from global_os.world.tools.repo_audit import run_repo_audit
from global_os.world.tools.repo_inventory import run_repo_inventory, verify_repo_inventory_report
from global_os.world.tools.research_scan import run_research_scan, verify_research_scan
from global_os.world.tools.workspace_io import (
    run_workspace_read_text,
    run_workspace_write_text,
    verify_workspace_read_text,
    verify_workspace_write_text,
)

ProduceFn = Callable[[Path, dict[str, Any], dict[str, Any]], dict[str, Any]]
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
    allowed_arg_keys: frozenset[str] = frozenset()
    require_empty_args: bool = True


class ToolCatalogError(Exception):
    pass


def _produce_repo_audit(
    target: Path, hooks: dict[str, Any], _args: dict[str, Any]
) -> dict[str, Any]:
    if hooks.get("inject_corrupt_report"):
        return {"findings": [], "modified_target": True}
    if hooks.get("inject_empty_report"):
        return {"findings": [], "read_only": True, "modified_target": False, "scan": {}}
    return run_repo_audit(target)


def _produce_repo_inventory(
    target: Path, hooks: dict[str, Any], _args: dict[str, Any]
) -> dict[str, Any]:
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


def _produce_workspace_read(
    target: Path, hooks: dict[str, Any], args: dict[str, Any]
) -> dict[str, Any]:
    path = str(hooks.get("read_path_override") or args.get("path") or "README.md")
    return run_workspace_read_text(target, rel_path=path)


def _produce_workspace_write(
    target: Path, hooks: dict[str, Any], args: dict[str, Any]
) -> dict[str, Any]:
    path = str(args.get("path") or "")
    content = str(args.get("content") or "")
    if hooks.get("inject_write_failure"):
        return {
            "kind": "workspace_write_text",
            "ok": False,
            "modified_target": False,
            "error": "injected_write_failure",
        }
    return run_workspace_write_text(target, rel_path=path, content=content)


def _produce_research_scan(
    target: Path, hooks: dict[str, Any], _args: dict[str, Any]
) -> dict[str, Any]:
    if hooks.get("inject_empty_report"):
        return {
            "kind": "research_scan",
            "read_only": True,
            "modified_target": False,
            "ok": True,
            "files_scanned": 0,
            "sources": [],
            "claims": [],
        }
    return run_research_scan(target)


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
            "research scan",
            "source inventory",
        ),
        require_empty_args=True,
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
            "research scan",
        ),
        require_empty_args=True,
    ),
    "workspace.read_text": OperatorToolSpec(
        tool_id="workspace.read_text",
        required_capabilities=("filesystem.read",),
        intended_effect="workspace_file_read",
        artifact_kind="workspace_read_text",
        desc_markers=(
            "read file",
            "inspect source",
            "open file",
            "read workspace file",
        ),
        exclude_markers=("write file", "research scan"),
        allowed_arg_keys=frozenset({"path"}),
        require_empty_args=False,
    ),
    "workspace.write_text": OperatorToolSpec(
        tool_id="workspace.write_text",
        required_capabilities=("filesystem.write",),
        intended_effect="workspace_file_write",
        artifact_kind="workspace_write_text",
        desc_markers=(
            "write file",
            "apply fix",
            "modify workspace",
            "patch file",
        ),
        exclude_markers=("read-only", "research scan", "audit report"),
        allowed_arg_keys=frozenset({"path", "content"}),
        require_empty_args=False,
    ),
    "research.scan": OperatorToolSpec(
        tool_id="research.scan",
        required_capabilities=("filesystem.read",),
        intended_effect="research_scan_report",
        artifact_kind="research_scan",
        desc_markers=(
            "research scan",
            "source inventory",
            "literature scan",
            "extract sources",
            "competing hypotheses",
        ),
        exclude_markers=("engineering report", "audit report", "write file"),
        require_empty_args=True,
    ),
}


TOOL_IMPL: dict[str, tuple[ProduceFn, VerifyFn]] = {
    "repo.audit": (_produce_repo_audit, verify_repo_audit_report),
    "repo.inventory": (_produce_repo_inventory, verify_repo_inventory_report),
    "workspace.read_text": (_produce_workspace_read, verify_workspace_read_text),
    "workspace.write_text": (_produce_workspace_write, verify_workspace_write_text),
    "research.scan": (_produce_research_scan, verify_research_scan),
}


def registered_tool_ids() -> frozenset[str]:
    return frozenset(OPERATOR_TOOL_SPECS)


def resolve_allowed_tool_ids(
    *,
    goal_capabilities: list[str] | set[str],
    brief_allowed_capabilities: list[str] | set[str],
) -> list[str]:
    """Tools whose required capabilities ⊆ goal ∩ brief allow-lists."""
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


def validate_tool_args(tool_id: str, args: Any) -> dict[str, Any]:
    """Fail-closed argument check — never silently ignore model args."""
    if tool_id not in OPERATOR_TOOL_SPECS:
        raise ToolCatalogError(f"unknown_tool_id:{tool_id}")
    spec = OPERATOR_TOOL_SPECS[tool_id]
    if args is None:
        args = {}
    if not isinstance(args, dict):
        raise ToolCatalogError("invalid_tool_args:not_object")
    keys = set(args)
    if spec.require_empty_args:
        if keys:
            raise ToolCatalogError("invalid_tool_args:expected_empty")
        return {}
    if not keys.issubset(spec.allowed_arg_keys):
        raise ToolCatalogError(
            f"invalid_tool_args:unexpected_keys:{sorted(keys - spec.allowed_arg_keys)}"
        )
    if tool_id == "workspace.read_text":
        path = args.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ToolCatalogError("invalid_tool_args:path_required")
        return {"path": path.strip()}
    if tool_id == "workspace.write_text":
        path = args.get("path")
        content = args.get("content")
        if not isinstance(path, str) or not path.strip():
            raise ToolCatalogError("invalid_tool_args:path_required")
        if not isinstance(content, str):
            raise ToolCatalogError("invalid_tool_args:content_required")
        return {"path": path.strip(), "content": content}
    return dict(args)


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
    tool_id: str,
    target: Path,
    hooks: dict[str, Any],
    *,
    args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if tool_id not in TOOL_IMPL:
        raise ToolCatalogError(f"unknown_tool_id:{tool_id}")
    produce, _verify = TOOL_IMPL[tool_id]
    return produce(target, hooks, dict(args or {}))


def verify_tool_artifact(tool_id: str, report: Any) -> dict[str, Any]:
    if tool_id not in TOOL_IMPL:
        return {"ok": False, "reason": f"unknown_tool_id:{tool_id}"}
    _produce, verify = TOOL_IMPL[tool_id]
    return verify(report)
