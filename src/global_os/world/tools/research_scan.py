"""Local research scan — extract source-like references from markdown/text."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".gos",
        "dist",
        "build",
    }
)
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+|[^)]+\.md)\)")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
MAX_FILES = 80
MAX_BYTES_PER_FILE = 32_000


def run_research_scan(root: Path, *, max_files: int = MAX_FILES) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        return {
            "kind": "research_scan",
            "read_only": True,
            "modified_target": False,
            "ok": False,
            "error": "root_not_directory",
            "sources": [],
            "claims": [],
        }
    sources: list[dict[str, str]] = []
    claims: list[dict[str, str]] = []
    files_scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".txt", ".rst"}:
            continue
        files_scanned += 1
        if files_scanned > max_files:
            break
        try:
            text = path.read_bytes()[:MAX_BYTES_PER_FILE].decode("utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(root))
        for label, href in LINK_RE.findall(text):
            sources.append({"file": rel, "label": label[:200], "href": href[:500]})
        for doi in DOI_RE.findall(text):
            sources.append({"file": rel, "label": "doi", "href": f"doi:{doi}"})
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("- ", "* ", "> ")) and len(stripped) > 40:
                claims.append({"file": rel, "text": stripped[:400], "epistemic": "unverified_claim"})
                if len(claims) >= 40:
                    break
        if len(claims) >= 40:
            break
    return {
        "kind": "research_scan",
        "read_only": True,
        "modified_target": False,
        "ok": True,
        "root": str(root),
        "files_scanned": files_scanned,
        "sources": sources[:100],
        "source_count": len(sources),
        "claims": claims[:40],
        "claim_count": len(claims),
        "note": "claims are extracted text spans, not verified facts",
    }


def verify_research_scan(report: Any) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {"ok": False, "reason": "report_not_object"}
    if report.get("kind") != "research_scan":
        return {"ok": False, "reason": "wrong_kind"}
    if report.get("modified_target") is not False:
        return {"ok": False, "reason": "modified_target_not_false"}
    if report.get("read_only") is not True:
        return {"ok": False, "reason": "read_only_not_true"}
    if report.get("ok") is not True:
        return {"ok": False, "reason": "scan_not_ok"}
    if not isinstance(report.get("sources"), list):
        return {"ok": False, "reason": "missing_sources"}
    if not isinstance(report.get("claims"), list):
        return {"ok": False, "reason": "missing_claims"}
    if int(report.get("files_scanned") or 0) < 1:
        return {"ok": False, "reason": "no_files_scanned"}
    sources = report.get("sources") or []
    claims = report.get("claims") or []
    # Empty evidence cannot satisfy research source/claim criteria (false SUCCESS).
    if len(sources) < 1:
        return {"ok": False, "reason": "empty_sources", "claim_count": len(claims)}
    if len(claims) < 1:
        return {"ok": False, "reason": "empty_claims", "source_count": len(sources)}
    return {
        "ok": True,
        "reason": "structure_ok",
        "source_count": len(sources),
        "claim_count": len(claims),
    }
