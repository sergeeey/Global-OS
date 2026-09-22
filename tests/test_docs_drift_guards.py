"""Docs/state drift guards — machine-readable SoT must not claim forbidden completions."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PHRASES = [
    r"M1\.5\s+complete",
    r"DoD\s*V2\s+complete",
    r"PRODUCTION_PROVEN\s+achieved",
]


def test_capability_matrix_has_no_production_proven_capability():
    matrix = json.loads((ROOT / "docs" / "capability_matrix.json").read_text(encoding="utf-8"))
    proven = [c["id"] for c in matrix["capabilities"] if c.get("state") == "PRODUCTION_PROVEN"]
    assert proven == [], f"capabilities must not claim PRODUCTION_PROVEN yet: {proven}"


def test_readme_and_status_avoid_forbidden_completion_claims():
    texts = [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "docs" / "IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8"),
        (ROOT / "ROADMAP.md").read_text(encoding="utf-8") if (ROOT / "ROADMAP.md").exists() else "",
    ]
    blob = "\n".join(texts)
    for pat in FORBIDDEN_PHRASES:
        assert re.search(pat, blob, flags=re.IGNORECASE) is None, f"forbidden claim matched: {pat}"


def test_rule_approximation_neq_contract_present():
    matrix = json.loads((ROOT / "docs" / "capability_matrix.json").read_text(encoding="utf-8"))
    assert "approximation" in matrix.get("rule", "").lower() or "≠" in matrix.get("rule", "") or "\u2260" in matrix.get(
        "rule", ""
    )
