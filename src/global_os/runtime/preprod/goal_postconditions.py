"""Goal-specific postconditions — tool success ≠ criterion satisfaction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from global_os.world.tools.workspace_io import resolve_under

# Filenames mentioned in criterion text (e.g. FIX_APPLIED.txt).
_FILE_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:txt|md|py|json|toml))(?![A-Za-z0-9_.-])"
)


def _criterion_entries(goal: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            out.append((c, c))
            continue
        cid = str(c.get("id") or "")
        desc = str(c.get("description") or "")
        if cid:
            out.append((cid, desc))
    return out


def expected_write_paths_for_criterion(description: str) -> list[str]:
    """Extract concrete filenames a write criterion requires."""
    found = _FILE_TOKEN_RE.findall(description or "")
    # Prefer explicit FIX_* / ACCEPT_* style tokens first.
    preferred = [f for f in found if f.upper().startswith(("FIX_", "ACCEPT_"))]
    return preferred or found


def postcondition_workspace_write(
    root: Path, report: dict[str, Any]
) -> dict[str, Any]:
    """Re-read disk after write — report alone is insufficient (GOS-I13)."""
    rel = str(report.get("path") or "")
    path = resolve_under(root, rel)
    if path is None:
        return {"ok": False, "reason": "path_escape_or_invalid", "path": rel}
    if not path.is_file():
        return {"ok": False, "reason": "file_missing_on_disk", "path": rel}
    try:
        on_disk = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "reason": f"read_failed:{exc}", "path": rel}
    expected = report.get("content")
    if not isinstance(expected, str):
        return {"ok": False, "reason": "report_missing_content", "path": rel}
    if on_disk != expected:
        return {
            "ok": False,
            "reason": "content_mismatch_on_disk",
            "path": rel,
            "disk_bytes": len(on_disk.encode("utf-8")),
            "report_bytes": len(expected.encode("utf-8")),
        }
    return {
        "ok": True,
        "reason": "disk_matches_report",
        "path": rel,
        "byte_length": len(on_disk.encode("utf-8")),
    }


def filter_write_criteria_by_goal(
    goal: dict[str, Any],
    *,
    candidate_ids: list[str],
    report: dict[str, Any],
    postcondition: dict[str, Any],
) -> list[str]:
    """Bind write criteria only when path+disk match Goal Contract tokens."""
    if not postcondition.get("ok"):
        return []
    written = str(report.get("path") or "")
    if not written:
        return []
    allowed: list[str] = []
    for cid, desc in _criterion_entries(goal):
        if cid not in candidate_ids:
            continue
        expected = expected_write_paths_for_criterion(desc)
        if not expected:
            # Write-related criterion without a concrete filename cannot be auto-met.
            continue
        if written in expected:
            allowed.append(cid)
    return allowed


def independent_accept_write_goal(
    goal: dict[str, Any], target: Path
) -> dict[str, Any]:
    """Filesystem oracle for write criteria — independent of Operator receipts."""
    checks: list[dict[str, Any]] = []
    met: list[str] = []
    unmet: list[str] = []
    for cid, desc in _criterion_entries(goal):
        expected = expected_write_paths_for_criterion(desc)
        lowered = desc.lower()
        if not expected and not any(
            m in lowered for m in ("write file", "apply fix", "fix_applied", "accept_")
        ):
            continue
        if not expected:
            unmet.append(cid)
            checks.append({"id": cid, "ok": False, "reason": "no_filename_in_criterion"})
            continue
        ok_any = False
        for rel in expected:
            path = resolve_under(target, rel)
            if path is not None and path.is_file() and path.stat().st_size > 0:
                ok_any = True
                checks.append({"id": cid, "ok": True, "path": rel})
                break
        if ok_any:
            met.append(cid)
        else:
            unmet.append(cid)
            checks.append(
                {
                    "id": cid,
                    "ok": False,
                    "reason": "required_file_absent",
                    "expected": expected,
                }
            )
    return {
        "met": met,
        "unmet": unmet,
        "checks": checks,
        "accept": bool(met) and not unmet,
    }
