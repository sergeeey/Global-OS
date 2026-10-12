"""PaperQA-style claim→citation→passage grounding (ADR-0013).

Citation-less claims cannot be promoted to verified. Contradictions are recorded
as epistemic edges, not LLM peer-review truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from global_os.verification.source import SourceClaim, verify_source_claim


@dataclass(frozen=True)
class GroundedCitation:
    source_path: str
    passage: str
    claim_statement: str


@dataclass(frozen=True)
class GroundingResult:
    grounded: bool
    citations: tuple[GroundedCitation, ...]
    contradictions: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounded": self.grounded,
            "citations": [
                {
                    "source_path": c.source_path,
                    "passage": c.passage,
                    "claim_statement": c.claim_statement,
                }
                for c in self.citations
            ],
            "contradictions": list(self.contradictions),
            "reason": self.reason,
        }


def ground_claim(
    *,
    statement: str,
    citations: list[dict[str, str]],
    root: Path,
    contradicting_passages: list[str] | None = None,
) -> GroundingResult:
    """Require ≥1 citation with passage present in source file."""
    if not citations:
        return GroundingResult(
            grounded=False,
            citations=(),
            contradictions=(),
            reason="citation_less_claim_rejected",
        )

    grounded_list: list[GroundedCitation] = []
    for cit in citations:
        path = cit.get("source_path") or ""
        passage = cit.get("passage") or ""
        if not path or not passage:
            return GroundingResult(
                grounded=False,
                citations=(),
                contradictions=(),
                reason="incomplete_citation",
            )
        outcome = verify_source_claim(
            SourceClaim(
                statement=statement,
                source_path=path,
                required_substring=passage,
            ),
            root=root,
        )
        if not outcome.passed:
            return GroundingResult(
                grounded=False,
                citations=(),
                contradictions=(),
                reason=str(outcome.details.get("reason", "passage_not_found")),
            )
        grounded_list.append(
            GroundedCitation(
                source_path=path, passage=passage, claim_statement=statement
            )
        )

    contradictions = tuple(contradicting_passages or ())
    if contradictions:
        return GroundingResult(
            grounded=False,
            citations=tuple(grounded_list),
            contradictions=contradictions,
            reason="contradiction_detected",
        )
    return GroundingResult(
        grounded=True,
        citations=tuple(grounded_list),
        contradictions=(),
        reason="grounded",
    )


def may_promote_claim(result: GroundingResult) -> bool:
    """Promotion gate — advisory LLM review is never sufficient alone."""
    return result.grounded and not result.contradictions
