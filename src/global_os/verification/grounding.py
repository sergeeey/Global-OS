"""PaperQA-style claim→citation→passage grounding (ADR-0013).

Citation-less claims cannot be promoted to verified. Contradictions are recorded
as epistemic edges, not LLM peer-review truth.

GOS-I08: passage presence in a source file is not enough — the *claim* must be
supported by the cited passage (claim coverage), not a coincidental substring.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from global_os.verification.source import SourceClaim, verify_source_claim

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


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


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def claim_supported_by_passage(statement: str, passage: str) -> bool:
    """True iff claim content is covered by the passage (not source-substring alone).

    Accepts: full claim ⊆ passage, passage ⊆ claim (short quote), or every
    content token (len≥2) of the claim appearing in the passage.
    """
    claim = _normalize_text(statement)
    pass_n = _normalize_text(passage)
    if not claim or not pass_n:
        return False
    if claim in pass_n or pass_n in claim:
        return True
    tokens = [t for t in _TOKEN_RE.findall(claim) if len(t) >= 2]
    if not tokens:
        return False
    return all(t in pass_n for t in tokens)


def ground_claim(
    *,
    statement: str,
    citations: list[dict[str, str]],
    root: Path,
    contradicting_passages: list[str] | None = None,
) -> GroundingResult:
    """Require ≥1 citation whose passage is in-source *and* supports the claim."""
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
        if not claim_supported_by_passage(statement, passage):
            return GroundingResult(
                grounded=False,
                citations=(),
                contradictions=(),
                reason="claim_not_supported_by_passage",
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
