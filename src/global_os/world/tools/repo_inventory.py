"""Read-only repository inventory tool — the second real MVP action."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SKIP_DIR_PARTS = frozenset(
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


def run_repo_inventory(root: Path, *, max_entries: int = 2000) -> dict[str, Any]:
    """Return a deterministic, read-only file inventory; never modify the target."""
    root = Path(root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"target directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"target is not a directory: {root}")
    entries = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in SKIP_DIR_PARTS for part in path.relative_to(root).parts)
    )
    return {
        "kind": "repo_inventory",
        "root": str(root),
        "file_count": len(entries),
        "entries": entries[:max_entries],
        "entries_truncated": len(entries) > max_entries,
        "read_only": True,
        "modified_target": False,
    }


def verify_repo_inventory_report(report: Any) -> dict[str, Any]:
    """Independent shape/integrity check for an inventory artifact."""
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("read_only") is not True:
        return {"ok": False, "reason": "read_only_not_true"}
    entries = report.get("entries")
    if not isinstance(entries, list):
        return {"ok": False, "reason": "missing_entries"}
    count = report.get("file_count")
    if not isinstance(count, int) or count < 0:
        return {"ok": False, "reason": "invalid_file_count"}
    if not report.get("entries_truncated") and count != len(entries):
        return {"ok": False, "reason": "file_count_mismatch"}
    return {"ok": True, "reason": "inventory_structure_ok", "file_count": count}
