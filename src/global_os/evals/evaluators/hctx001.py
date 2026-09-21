"""H-CTX-001 synthetic harness — structured context vs repeated compaction.

Verdict stays INCONCLUSIVE_NEEDS_REAL_MODEL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from global_os.cognition.context import ContextAssembler


@dataclass(frozen=True)
class Fact:
    fact_id: str
    token_cost: int
    critical: bool


FACTS: tuple[Fact, ...] = (
    Fact("goal", 30, True),
    Fact("obs_invoice", 40, True),
    Fact("bel_unpaid", 25, True),
    Fact("noise_chat", 80, False),
    Fact("old_summary", 60, False),
    Fact("cap_stripe", 20, True),
)


def _compaction_retention(round_n: int) -> set[str]:
    """Naive repeated summary: loses mid-horizon critical facts over rounds."""
    retained = {f.fact_id for f in FACTS}
    # each compaction drops oldest non-goal critical with some probability → deterministic drop
    drop_order = ["obs_invoice", "bel_unpaid", "cap_stripe", "noise_chat", "old_summary"]
    for i in range(min(round_n, len(drop_order))):
        retained.discard(drop_order[i])
    retained.add("goal")
    return retained


def _structured_retention(token_budget: int) -> set[str]:
    candidates = [
        {
            "source": f.fact_id,
            "type": "observation" if f.fact_id.startswith("obs") else "belief",
            "trust": "ORG_TRUSTED" if f.critical else "EXTERNAL_UNTRUSTED",
            "token_cost": f.token_cost,
            "reason_included": "critical" if f.critical else "noise",
            "priority": 1 if f.critical else 50,
        }
        for f in FACTS
    ]
    items = ContextAssembler().assemble(
        goal_id="goal_x", token_budget=token_budget, candidates=candidates
    )
    return {i["source"] for i in items}


def summarize_h_ctx_001() -> dict[str, Any]:
    critical_ids = {f.fact_id for f in FACTS if f.critical}
    compact_r3 = _compaction_retention(3)
    structured = _structured_retention(120)
    compact_integrity = len(critical_ids & compact_r3) / len(critical_ids)
    structured_integrity = len(critical_ids & structured) / len(critical_ids)
    return {
        "id": "H-CTX-001",
        "hypothesis": (
            "Typed retrieval from state/evidence/memory beats repeated conversation "
            "compaction on long-horizon state integrity."
        ),
        "fidelity": "synthetic_deterministic",
        "preregistered_at": "2026-09-21",
        "ran_at": datetime.now(UTC).isoformat(),
        "metrics": {
            "compaction_round3_critical_retention": round(compact_integrity, 4),
            "structured_critical_retention": round(structured_integrity, 4),
            "compaction_retained": sorted(compact_r3),
            "structured_retained": sorted(structured),
        },
        "synthetic_hint_structured_better": structured_integrity > compact_integrity,
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "note": "conversation context ≠ memory; harness validates assembler plumbing.",
    }
