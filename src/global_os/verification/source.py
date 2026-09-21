"""Source-derived verification protocol (resolve → retrieve → support → freshness)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from global_os.verification.router import (
    ResultClass,
    VerificationOutcome,
    VerificationTier,
)


@dataclass(frozen=True)
class SourceClaim:
    statement: str
    source_path: str
    required_substring: str


def verify_source_claim(claim: SourceClaim, *, root: Path) -> VerificationOutcome:
    path = (root / claim.source_path).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return VerificationOutcome(
            protocol="source_resolve_retrieve",
            tier=VerificationTier.INDEPENDENT,
            passed=False,
            details={"reason": "path escapes root"},
            diversity_factors=("different_source",),
        )
    if not path.is_file():
        return VerificationOutcome(
            protocol="source_resolve_retrieve",
            tier=VerificationTier.INDEPENDENT,
            passed=False,
            details={"reason": "source not found", "path": str(path)},
            diversity_factors=("different_source",),
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    supported = claim.required_substring in text
    return VerificationOutcome(
        protocol="source_resolve_retrieve",
        tier=VerificationTier.INDEPENDENT,
        passed=supported,
        details={
            "result_class": ResultClass.SOURCE_DERIVED.value,
            "source_path": claim.source_path,
            "supported": supported,
        },
        diversity_factors=("different_source", "different_codebase"),
    )
