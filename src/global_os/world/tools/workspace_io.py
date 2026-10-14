"""Sandbox workspace read/write tools for PREPROD_SUPERVISED missions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_READ_BYTES = 64_000
MAX_WRITE_BYTES = 64_000


def _resolve_under(root: Path, rel: str) -> Path | None:
    if not rel or rel.startswith("/") or ".." in Path(rel).parts:
        return None
    root = root.resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def run_workspace_read_text(root: Path, *, rel_path: str) -> dict[str, Any]:
    path = _resolve_under(root, rel_path)
    if path is None:
        return {
            "kind": "workspace_read_text",
            "read_only": True,
            "modified_target": False,
            "ok": False,
            "error": "path_escape_or_invalid",
        }
    if not path.is_file():
        return {
            "kind": "workspace_read_text",
            "read_only": True,
            "modified_target": False,
            "ok": False,
            "error": "not_a_file",
            "path": rel_path,
        }
    data = path.read_bytes()
    truncated = len(data) > MAX_READ_BYTES
    text = data[:MAX_READ_BYTES].decode("utf-8", errors="replace")
    return {
        "kind": "workspace_read_text",
        "read_only": True,
        "modified_target": False,
        "ok": True,
        "path": rel_path,
        "byte_length": len(data),
        "truncated": truncated,
        "content": text,
    }


def verify_workspace_read_text(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("kind") != "workspace_read_text":
        return {"ok": False, "reason": "wrong_kind"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("ok") is not True:
        return {"ok": False, "reason": str(report.get("error") or "read_failed")}
    if not isinstance(report.get("content"), str):
        return {"ok": False, "reason": "missing_content"}
    return {"ok": True, "reason": "read_ok", "path": report.get("path")}


def run_workspace_write_text(
    root: Path, *, rel_path: str, content: str
) -> dict[str, Any]:
    path = _resolve_under(root, rel_path)
    if path is None:
        return {
            "kind": "workspace_write_text",
            "read_only": False,
            "modified_target": False,
            "ok": False,
            "error": "path_escape_or_invalid",
        }
    if not isinstance(content, str):
        return {
            "kind": "workspace_write_text",
            "read_only": False,
            "modified_target": False,
            "ok": False,
            "error": "content_not_string",
        }
    raw = content.encode("utf-8")
    if len(raw) > MAX_WRITE_BYTES:
        return {
            "kind": "workspace_write_text",
            "read_only": False,
            "modified_target": False,
            "ok": False,
            "error": "content_too_large",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {
        "kind": "workspace_write_text",
        "read_only": False,
        "modified_target": True,
        "ok": True,
        "path": rel_path,
        "byte_length": len(raw),
    }


def verify_workspace_write_text(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("kind") != "workspace_write_text":
        return {"ok": False, "reason": "wrong_kind"}
    if report.get("ok") is not True:
        return {"ok": False, "reason": str(report.get("error") or "write_failed")}
    if report.get("modified_target") is not True:
        return {"ok": False, "reason": "modified_target_not_true"}
    return {"ok": True, "reason": "write_ok", "path": report.get("path")}
