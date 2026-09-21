"""H-ENV live ladder experiment contract (A→E). E is not required to win."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from global_os.adapters.models.base import GenerateRequest, ModelProvider, ModelProviderError
from global_os.adapters.models.recording import RecordingModelProvider
from global_os.runtime.events.ledger import EventLedger

LadderLevel = Literal["A", "B", "C", "D", "E"]

LADDER: tuple[tuple[LadderLevel, str], ...] = (
    ("A", "model_only"),
    ("B", "model_plus_tools"),
    ("C", "B_plus_environment_compiler"),
    ("D", "C_plus_epistemic_kernel"),
    ("E", "full_global_os"),
)

SCORE_FIELDS: tuple[str, ...] = (
    "goal_success",
    "escaped_errors",
    "evidence_precision",
    "unsupported_claims",
    "human_interventions",
    "cost",
    "latency",
    "tool_calls",
    "recovery_events",
)


@dataclass
class LadderTrial:
    level: LadderLevel
    label: str
    scores: dict[str, float]
    model_calls: int
    notes: str = ""


@dataclass
class HEnvExperimentReport:
    hypothesis: str = "H-ENV-001"
    fidelity: str = "PROVIDER_WIRE"
    same_model_family: bool = True
    same_monetary_budget: bool = True
    trials: list[LadderTrial] = field(default_factory=list)
    winner: LadderLevel | None = None
    e_required_to_win: bool = False
    scientific_claim_accepted: bool = False
    verdict: str = "INCONCLUSIVE"
    recorded_at: str = ""
    limitations: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis": self.hypothesis,
            "fidelity": self.fidelity,
            "same_model_family": self.same_model_family,
            "same_monetary_budget": self.same_monetary_budget,
            "ladder": [{"level": lv, "label": lb} for lv, lb in LADDER],
            "score_fields": list(SCORE_FIELDS),
            "trials": [asdict(t) for t in self.trials],
            "winner": self.winner,
            "e_required_to_win": self.e_required_to_win,
            "scientific_claim_accepted": self.scientific_claim_accepted,
            "verdict": self.verdict,
            "recorded_at": self.recorded_at,
            "limitations": self.limitations,
            "rule": "Do not require E to win; simple configs beating E is a valid result",
        }


def _level_prompt(level: LadderLevel, task: str) -> str:
    hints = {
        "A": "Answer using only reasoning. No tools.",
        "B": "You may assume tools exist; still answer briefly.",
        "C": "Assume Environment Compiler structured the workspace.",
        "D": "Assume Epistemic Kernel tracks evidence vs claims.",
        "E": "Assume full Global OS (authority, verification, durable runtime).",
    }
    return f"{hints[level]}\nTask: {task}\nReply with the final answer only."


def _score_reply(text: str, expect: str) -> dict[str, float]:
    ok = expect.strip().upper() in text.strip().upper()
    return {
        "goal_success": 1.0 if ok else 0.0,
        "escaped_errors": 0.0 if ok else 1.0,
        "evidence_precision": 1.0 if ok else 0.0,
        "unsupported_claims": 0.0 if ok else 1.0,
        "human_interventions": 0.0,
        "cost": 0.0,
        "latency": 0.0,
        "tool_calls": 0.0,
        "recovery_events": 0.0,
    }


def run_henv_ladder(
    provider: ModelProvider,
    *,
    task: str = "What is 21*19? Integer only.",
    expect: str = "399",
    fidelity: str = "PROVIDER_WIRE",
) -> HEnvExperimentReport:
    """Run A–E ladder with same provider/task. E need not win."""
    ledger = EventLedger()
    recorded = RecordingModelProvider(provider, ledger, goal_id="goal_henv_ladder")
    trials: list[LadderTrial] = []
    for level, label in LADDER:
        try:
            resp = recorded.generate(
                GenerateRequest(prompt=_level_prompt(level, task), max_tokens=32, temperature=0.0)
            )
            scores = _score_reply(resp.text, expect)
            scores["cost"] = float(resp.cost_usd or 0.0)
            scores["latency"] = float(resp.latency_ms)
            trials.append(
                LadderTrial(
                    level=level, label=label, scores=scores, model_calls=1, notes=resp.text[:80]
                )
            )
        except ModelProviderError as exc:
            scores = {f: 0.0 for f in SCORE_FIELDS}
            scores["escaped_errors"] = 1.0
            trials.append(
                LadderTrial(
                    level=level, label=label, scores=scores, model_calls=0, notes=str(exc)[:120]
                )
            )

    # Utility = goal_success - 0.2*escaped_errors - cost_norm; do not prefer E a priori
    def utility(t: LadderTrial) -> float:
        return t.scores["goal_success"] - 0.2 * t.scores["escaped_errors"] - 10.0 * t.scores["cost"]

    winner = max(trials, key=utility).level if trials else None
    return HEnvExperimentReport(
        fidelity=fidelity,
        trials=trials,
        winner=winner,
        e_required_to_win=False,
        scientific_claim_accepted=False,
        verdict=(
            "WIRE_LADDER_OK_NOT_SCIENTIFIC"
            if fidelity.startswith(("PROVIDER", "WIRE"))
            else "LIVE_MEASURED_INCONCLUSIVE"
        ),
        recorded_at=datetime.now(UTC).isoformat(),
        limitations=(
            "Single micro-task ladder; not frontier long-horizon proof. "
            "Levels B–E are prompt-conditioned until full tool/env wiring is live."
        ),
    )
