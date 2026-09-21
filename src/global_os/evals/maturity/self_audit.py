"""Capability self-audit — dogfood Epistemic Kernel on Global OS maturity claims."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

Maturity = Literal[
    "CONTRACTED",
    "STUBBED",
    "STATICALLY_IMPLEMENTED",
    "RUNTIME_VERIFIED_HARNESS",
    "RUNTIME_VERIFIED_LOCAL",
    "INTEGRATION_VERIFIED",
    "OPERATIONALLY_VALIDATED",
    "PRODUCTION_PROVEN",
]


@dataclass
class CapabilityAuditRow:
    capability: str
    claim: str
    implementation: bool
    tests: bool
    runtime_evidence: bool
    adversarial_evidence: bool
    long_horizon_evidence: bool
    external_evidence: bool
    matrix_state: str
    maturity: Maturity
    overstated: bool
    notes: str = ""


def _infer_maturity(row_flags: dict[str, bool], matrix_state: str) -> Maturity:
    if matrix_state == "PRODUCTION_PROVEN":
        return "PRODUCTION_PROVEN"
    if row_flags["long_horizon_evidence"] and row_flags["runtime_evidence"]:
        return "OPERATIONALLY_VALIDATED"
    if row_flags["runtime_evidence"] and row_flags["adversarial_evidence"]:
        return "INTEGRATION_VERIFIED"
    if matrix_state.startswith("RUNTIME_VERIFIED"):
        return "RUNTIME_VERIFIED_HARNESS" if "HARNESS" in matrix_state else "RUNTIME_VERIFIED_LOCAL"
    if row_flags["implementation"] and row_flags["tests"]:
        return "STATICALLY_IMPLEMENTED"
    if row_flags["implementation"]:
        return "STUBBED"
    return "CONTRACTED"


def _overstated(claim: str, maturity: Maturity) -> bool:
    lowered = claim.lower()
    if "production" in lowered and maturity != "PRODUCTION_PROVEN":
        return True
    return "production-safe" in lowered and maturity not in {
        "OPERATIONALLY_VALIDATED",
        "PRODUCTION_PROVEN",
    }


def audit_capability_matrix(matrix_path: Path | None = None) -> dict[str, Any]:
    if matrix_path is None:
        here = Path(__file__).resolve()
        root = next(p for p in here.parents if (p / "docs" / "capability_matrix.json").exists())
        path = root / "docs" / "capability_matrix.json"
    else:
        path = matrix_path
    matrix = json.loads(path.read_text(encoding="utf-8"))
    rows: list[CapabilityAuditRow] = []
    for item in matrix["capabilities"]:
        state = item["state"]
        evidence = str(item.get("evidence", ""))
        claim = f"{item['id']}={state}"
        flags = {
            "implementation": state not in {"CONTRACTED", "STUBBED"},
            "tests": "tests/" in evidence or "test_" in evidence,
            "runtime_evidence": state.startswith("RUNTIME_VERIFIED") or "HARNESS" in state,
            "adversarial_evidence": "survival" in item["id"] or "survival" in evidence.lower(),
            "long_horizon_evidence": "48h" in evidence.lower() or "soak" in evidence.lower(),
            "external_evidence": "collector" in evidence.lower() or "docker" in evidence.lower(),
        }
        # Long-horizon only true for soak capability itself when wall not claimed
        if "48h" in item["id"] and "not PRODUCTION_PROVEN" in evidence:
            flags["long_horizon_evidence"] = False
        maturity = _infer_maturity(flags, state)
        over = _overstated(claim + " " + evidence, maturity)
        rows.append(
            CapabilityAuditRow(
                capability=item["id"],
                claim=claim,
                implementation=flags["implementation"],
                tests=flags["tests"],
                runtime_evidence=flags["runtime_evidence"],
                adversarial_evidence=flags["adversarial_evidence"],
                long_horizon_evidence=flags["long_horizon_evidence"],
                external_evidence=flags["external_evidence"],
                matrix_state=state,
                maturity=maturity,
                overstated=over,
                notes="CLAIM OVERSTATED" if over else "",
            )
        )

    overstated = [r.capability for r in rows if r.overstated]
    return {
        "schema_version": "0.1.0",
        "audited_at": datetime.now(UTC).isoformat(),
        "capability_count": len(rows),
        "overstated_count": len(overstated),
        "overstated": overstated,
        "rows": [asdict(r) for r in rows],
        "rule": "README/matrix claim without evidence ⇒ CLAIM OVERSTATED",
    }
