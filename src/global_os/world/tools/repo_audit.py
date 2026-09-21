"""Read-only repository audit toolset (first killer use case)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RepoAuditFinding:
    id: str
    area: str
    severity: str
    statement: str
    evidence_path: str


def scan_repo_structure(root: Path) -> dict[str, Any]:
    """Collect structural signals — no writes to target repo."""
    root = root.resolve()
    files = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    # ignore heavy/noise dirs
    skip = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache", ".gos"}
    files = [f for f in files if not any(part in skip for part in f.split("/"))]
    return {
        "root": str(root),
        "file_count": len(files),
        "has_constitution": "CONSTITUTION.md" in files,
        "has_schemas": any(f.startswith("contracts/schemas/") for f in files),
        "has_tests": any(f.startswith("tests/") for f in files),
        "has_ci": any(f.startswith(".github/workflows/") for f in files),
        "sample_files": sorted(files)[:50],
    }


def build_findings(scan: dict[str, Any]) -> list[RepoAuditFinding]:
    findings: list[RepoAuditFinding] = []
    if scan.get("has_constitution"):
        findings.append(
            RepoAuditFinding(
                id="f_constitution",
                area="architecture",
                severity="info",
                statement="CONSTITUTION.md present — invariants documented",
                evidence_path="CONSTITUTION.md",
            )
        )
    else:
        findings.append(
            RepoAuditFinding(
                id="f_missing_constitution",
                area="architecture",
                severity="high",
                statement="CONSTITUTION.md missing",
                evidence_path=".",
            )
        )
    if not scan.get("has_tests"):
        findings.append(
            RepoAuditFinding(
                id="f_no_tests",
                area="testing",
                severity="high",
                statement="No tests/ directory detected",
                evidence_path=".",
            )
        )
    if scan.get("has_schemas"):
        findings.append(
            RepoAuditFinding(
                id="f_schemas",
                area="contracts",
                severity="info",
                statement="JSON schemas present under contracts/schemas",
                evidence_path="contracts/schemas",
            )
        )
    return findings


def run_repo_audit(root: Path) -> dict[str, Any]:
    scan = scan_repo_structure(root)
    findings = [f.__dict__ for f in build_findings(scan)]
    return {
        "scan": scan,
        "findings": findings,
        "read_only": True,
        "modified_target": False,
    }
