"""Read-only repository audit toolset (first killer use case).

Depth levels:
- structure: file presence signals only
- deep: content-level deterministic checks (invariants, forbidden patterns,
  schema inventory, provider boundary heuristics). Not an LLM security audit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

AuditDepth = Literal["structure", "deep"]

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

# Markers expected in CONSTITUTION for Global OS binding invariants.
REQUIRED_INVARIANTS = tuple(f"GOS-I{i:02d}" for i in range(1, 26))

# Forbidden patterns from AGENTS.md / CONSTITUTION spirit — static heuristics.
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "execute_anything",
        re.compile(r"agent\.execute_anything\s*\(|Bash\s*\(\s*\*\s*\)"),
        "Unbounded execute_anything / Bash(*) is forbidden",
    ),
    (
        "silent_allow_fallback",
        re.compile(
            r"except\s+[A-Za-z_][\w.]*\s*:\s*(?:pass\s*$|return\s+True\b|return\s+[\"']ALLOW)",
            re.MULTILINE,
        ),
        "Silent allow/pass on exception looks like fail-open",
    ),
)

# Provider SDKs must live under adapters/models (heuristic).
PROVIDER_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(openai|anthropic|google\.generativeai|cohere)\b",
    re.MULTILINE,
)
ALLOWED_PROVIDER_PREFIXES = (
    "src/global_os/adapters/models/",
    "tests/",
)


@dataclass(frozen=True)
class RepoAuditFinding:
    id: str
    area: str
    severity: str
    statement: str
    evidence_path: str


def _list_files(root: Path) -> list[str]:
    root = root.resolve()
    files = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    return [f for f in files if not any(part in SKIP_DIR_PARTS for part in f.split("/"))]


def scan_repo_structure(root: Path) -> dict[str, Any]:
    """Collect structural signals — no writes to target repo."""
    root = root.resolve()
    files = _list_files(root)
    return {
        "root": str(root),
        "file_count": len(files),
        "has_constitution": "CONSTITUTION.md" in files,
        "has_schemas": any(f.startswith("contracts/schemas/") for f in files),
        "has_tests": any(f.startswith("tests/") for f in files),
        "has_ci": any(f.startswith(".github/workflows/") for f in files),
        "sample_files": sorted(files)[:50],
    }


def scan_invariant_coverage(root: Path) -> dict[str, Any]:
    path = root / "CONSTITUTION.md"
    if not path.is_file():
        return {
            "present": False,
            "required": list(REQUIRED_INVARIANTS),
            "found": [],
            "missing": list(REQUIRED_INVARIANTS),
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    found = [inv for inv in REQUIRED_INVARIANTS if inv in text]
    missing = [inv for inv in REQUIRED_INVARIANTS if inv not in text]
    return {
        "present": True,
        "required": list(REQUIRED_INVARIANTS),
        "found": found,
        "missing": missing,
        "coverage": len(found) / len(REQUIRED_INVARIANTS),
    }


def scan_forbidden_patterns(root: Path) -> dict[str, Any]:
    """Scan production Python under src/ for forbidden call patterns.

    Skips tests/ and this audit module (which documents the patterns).
    """
    hits: list[dict[str, Any]] = []
    for rel in _list_files(root):
        if not rel.endswith(".py"):
            continue
        if not rel.startswith("src/"):
            continue
        if rel.endswith("world/tools/repo_audit.py"):
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern_id, regex, message in FORBIDDEN_PATTERNS:
            for match in regex.finditer(text):
                # Ignore string/comment documentation of the forbidden form.
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_text = text[line_start : text.find("\n", match.start())]
                stripped = line_text.lstrip()
                if stripped.startswith(("#", '"', "'")):
                    continue
                if "FORBIDDEN" in line_text or "deny" in line_text.lower():
                    continue
                line = text.count("\n", 0, match.start()) + 1
                hits.append(
                    {
                        "pattern_id": pattern_id,
                        "path": rel,
                        "line": line,
                        "snippet": match.group(0)[:120],
                        "message": message,
                    }
                )
    return {"hit_count": len(hits), "hits": hits}


def scan_schema_inventory(root: Path) -> dict[str, Any]:
    schema_dir = root / "contracts" / "schemas"
    if not schema_dir.is_dir():
        return {"present": False, "count": 0, "names": []}
    names = sorted(p.name for p in schema_dir.glob("*.json"))
    return {"present": True, "count": len(names), "names": names}


def scan_provider_boundary(root: Path) -> dict[str, Any]:
    """Flag direct provider SDK imports outside adapters/models (and tests)."""
    violations: list[dict[str, str]] = []
    for rel in _list_files(root):
        if not rel.endswith(".py"):
            continue
        if any(rel.startswith(p) for p in ALLOWED_PROVIDER_PREFIXES):
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = PROVIDER_IMPORT_RE.search(text)
        if match:
            violations.append(
                {
                    "path": rel,
                    "provider": match.group(1),
                    "message": "provider SDK import outside adapters/models",
                }
            )
    return {"violation_count": len(violations), "violations": violations}


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


def build_deep_findings(deep: dict[str, Any]) -> list[RepoAuditFinding]:
    findings: list[RepoAuditFinding] = []
    inv = deep.get("invariants", {})
    missing = inv.get("missing") or []
    if inv.get("present") and not missing:
        findings.append(
            RepoAuditFinding(
                id="f_invariants_complete",
                area="constitution",
                severity="info",
                statement=f"All {len(REQUIRED_INVARIANTS)} GOS-Ixx markers present in CONSTITUTION",
                evidence_path="CONSTITUTION.md",
            )
        )
    elif missing:
        findings.append(
            RepoAuditFinding(
                id="f_invariants_missing",
                area="constitution",
                severity="high",
                statement=f"Missing invariant markers: {', '.join(missing[:8])}",
                evidence_path="CONSTITUTION.md",
            )
        )

    forbidden = deep.get("forbidden_patterns", {})
    for hit in forbidden.get("hits") or []:
        findings.append(
            RepoAuditFinding(
                id=f"f_forbidden_{hit['pattern_id']}_{hit['line']}",
                area="policy",
                severity="critical",
                statement=hit["message"],
                evidence_path=f"{hit['path']}:{hit['line']}",
            )
        )

    schemas = deep.get("schemas", {})
    if schemas.get("present") and schemas.get("count", 0) > 0:
        findings.append(
            RepoAuditFinding(
                id="f_schema_inventory",
                area="contracts",
                severity="info",
                statement=f"{schemas['count']} JSON schema files inventoried",
                evidence_path="contracts/schemas",
            )
        )

    boundary = deep.get("provider_boundary", {})
    for viol in boundary.get("violations") or []:
        findings.append(
            RepoAuditFinding(
                id=f"f_provider_boundary_{Path(viol['path']).stem}",
                area="adapters",
                severity="high",
                statement=viol["message"],
                evidence_path=viol["path"],
            )
        )
    if boundary.get("violation_count") == 0:
        findings.append(
            RepoAuditFinding(
                id="f_provider_boundary_clean",
                area="adapters",
                severity="info",
                statement="No direct provider SDK imports outside adapters/models",
                evidence_path="src/",
            )
        )
    return findings


def run_repo_audit(root: Path, *, depth: AuditDepth = "deep") -> dict[str, Any]:
    scan = scan_repo_structure(root)
    findings = build_findings(scan)
    deep: dict[str, Any] | None = None
    if depth == "deep":
        deep = {
            "invariants": scan_invariant_coverage(root),
            "forbidden_patterns": scan_forbidden_patterns(root),
            "schemas": scan_schema_inventory(root),
            "provider_boundary": scan_provider_boundary(root),
        }
        findings.extend(build_deep_findings(deep))
    return {
        "scan": scan,
        "deep": deep,
        "depth": depth,
        "findings": [f.__dict__ for f in findings],
        "read_only": True,
        "modified_target": False,
        # Honesty: deterministic static analysis ≠ LLM/security penetration audit
        "audit_kind": "deterministic_static",
    }
