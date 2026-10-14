"""Read-only workspace inventory tool (second Operator tool — Fork B Phase 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SKIP = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".gos",
        "target",
        "dist",
        "build",
    }
)


def run_repo_inventory(root: Path, *, max_entries: int = 200) -> dict[str, Any]:
    """List top-level entries under root — never writes."""
    root = root.resolve()
    if not root.is_dir():
        return {
            "kind": "repo_inventory",
            "read_only": True,
            "modified_target": False,
            "entries": [],
            "error": "root_not_directory",
        }
    entries: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.name in SKIP:
            continue
        entries.append(
            {
                "name": child.name,
                "is_dir": child.is_dir(),
                "is_file": child.is_file(),
            }
        )
        if len(entries) >= max_entries:
            break
    return {
        "kind": "repo_inventory",
        "read_only": True,
        "modified_target": False,
        "root": str(root),
        "entries": entries,
        "entry_count": len(entries),
        "truncated": len(entries) >= max_entries,
    }


def verify_repo_inventory_report(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("read_only") is not True:
        return {"ok": False, "reason": "read_only_not_true"}
    if report.get("kind") != "repo_inventory":
        return {"ok": False, "reason": "wrong_kind"}
    entries = report.get("entries")
    if not isinstance(entries, list) or len(entries) < 1:
        return {"ok": False, "reason": "empty_or_missing_entries"}
    return {
        "ok": True,
        "reason": "deterministic_structure_ok",
        "entry_count": len(entries),
    }
