"""H-RSN experiment: fixed-low/medium/high vs adaptive under fixed VerificationRequirement."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from global_os.cognition.metareasoning import ReasoningBudgetController

EFFORT_COST = {"low": 1.0, "medium": 2.0, "high": 4.0}
# Useful work proxy (0..1) — not raw accuracy idol
EFFORT_USEFUL = {"low": 0.50, "medium": 0.72, "high": 0.85}


@dataclass
class RsnTrial:
    policy: str
    effort: str
    verified_useful_work: float
    cost: float
    vuw_per_cost: float
    verification_tier: int


@dataclass
class HRsnExperimentReport:
    hypothesis: str = "H-RSN-001"
    fidelity: str = "synthetic_or_provider"
    verification_requirement_fixed: int = 2
    trials: list[RsnTrial] = field(default_factory=list)
    best_policy: str | None = None
    scientific_claim_accepted: bool = False
    verdict: str = "INCONCLUSIVE"
    gos_i23_ok: bool = True
    recorded_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis": self.hypothesis,
            "fidelity": self.fidelity,
            "primary_metric": "VerifiedUsefulWork/Cost",
            "verification_requirement_fixed": self.verification_requirement_fixed,
            "trials": [asdict(t) for t in self.trials],
            "best_policy": self.best_policy,
            "scientific_claim_accepted": self.scientific_claim_accepted,
            "verdict": self.verdict,
            "gos_i23_ok": self.gos_i23_ok,
            "recorded_at": self.recorded_at,
            "rule": "ReasoningBudget ≠ VerificationRequirement (GOS-I23)",
        }


def run_hrsn_policies(
    *,
    verification_tier: int = 2,
    signals_easy: set[str] | None = None,
    signals_hard: set[str] | None = None,
    fidelity: str = "synthetic_deterministic",
) -> HRsnExperimentReport:
    """Compare fixed-low/medium/high vs adaptive; VR fixed across policies."""
    easy = signals_easy or {"deterministic_task", "confidence_high"}
    hard = signals_hard or {"uncertainty_high", "task_high_impact"}
    ctrl = ReasoningBudgetController()
    policy = {
        "default_effort": "medium",
        "min_effort": "low",
        "max_effort": "high",
        "increase_when": ["verification_failed", "uncertainty_high", "task_high_impact"],
        "decrease_when": ["deterministic_task", "confidence_high", "cheap_verification_available"],
    }
    trials: list[RsnTrial] = []
    gos_ok = True

    for name, effort in (("fixed_low", "low"), ("fixed_medium", "medium"), ("fixed_high", "high")):
        # Mix: half easy / half hard → average useful work
        u = EFFORT_USEFUL[effort]
        c = EFFORT_COST[effort]
        trials.append(RsnTrial(name, effort, u, c, round(u / c, 4), verification_tier))

    # Adaptive: easy→low, hard→high; average VUW/cost across regimes
    d_easy = ctrl.decide(policy, verification_tier=verification_tier, signals=easy)
    d_hard = ctrl.decide(policy, verification_tier=verification_tier, signals=hard)
    if (
        d_easy.verification_tier_unchanged != verification_tier
        or d_hard.verification_tier_unchanged != verification_tier
    ):
        gos_ok = False
    u_avg = (EFFORT_USEFUL.get(d_easy.effort, 0.5) + EFFORT_USEFUL.get(d_hard.effort, 0.5)) / 2
    c_avg = (EFFORT_COST.get(d_easy.effort, 1.0) + EFFORT_COST.get(d_hard.effort, 1.0)) / 2
    trials.append(
        RsnTrial(
            "adaptive",
            f"{d_easy.effort}/{d_hard.effort}",
            u_avg,
            c_avg,
            round(u_avg / c_avg, 4),
            verification_tier,
        )
    )

    best = max(trials, key=lambda t: t.vuw_per_cost)
    return HRsnExperimentReport(
        fidelity=fidelity,
        verification_requirement_fixed=verification_tier,
        trials=trials,
        best_policy=best.policy,
        scientific_claim_accepted=False,
        verdict="HARNESS_OK_NOT_SCIENTIFIC" if gos_ok else "GOS_I23_VIOLATION",
        gos_i23_ok=gos_ok,
        recorded_at=datetime.now(UTC).isoformat(),
    )


DEFAULT_HRSN_TASKS: tuple[dict[str, str], ...] = (
    {"id": "arith", "prompt": "What is 12*11? Integer only.", "expect": "132", "signals": "easy"},
    {
        "id": "logic",
        "prompt": "If all A are B and all B are C, are all A C? Reply YES or NO.",
        "expect": "YES",
        "signals": "hard",
    },
    {
        "id": "extract",
        "prompt": "Extract year from: Global OS report 2026. Reply year only.",
        "expect": "2026",
        "signals": "easy",
    },
)


def run_hrsn_measured(
    provider: Any,
    *,
    tasks: tuple[dict[str, str], ...] | None = None,
    verification_tier: int = 2,
    fidelity: str = "PROVIDER_WIRE",
) -> dict[str, Any]:
    """Real model calls for fixed-low/medium/high vs adaptive; VR fixed (GOS-I23).

    scientific_claim_accepted stays False until live long-horizon evidence.
    """
    from global_os.adapters.models.base import GenerateRequest, ModelProvider, ModelProviderError

    if not isinstance(provider, ModelProvider):
        raise TypeError("provider must implement ModelProvider")

    task_set = tasks or DEFAULT_HRSN_TASKS
    ctrl = ReasoningBudgetController()
    budget_policy = {
        "default_effort": "medium",
        "min_effort": "low",
        "max_effort": "high",
        "increase_when": ["verification_failed", "uncertainty_high", "task_high_impact"],
        "decrease_when": ["deterministic_task", "confidence_high", "cheap_verification_available"],
    }
    policies: list[tuple[str, str | None]] = [
        ("fixed_low", "low"),
        ("fixed_medium", "medium"),
        ("fixed_high", "high"),
        ("adaptive", None),
    ]
    trial_rows: list[dict[str, Any]] = []
    gos_ok = True

    for policy_name, fixed_effort in policies:
        successes = 0
        tokens = 0
        latency = 0.0
        cost = 0.0
        calls = 0
        failures = 0
        efforts: list[str] = []
        for task in task_set:
            if fixed_effort is not None:
                effort = fixed_effort
            else:
                signals = (
                    {"deterministic_task", "confidence_high"}
                    if task.get("signals") == "easy"
                    else {"uncertainty_high", "task_high_impact"}
                )
                decision = ctrl.decide(
                    budget_policy, verification_tier=verification_tier, signals=signals
                )
                if decision.verification_tier_unchanged != verification_tier:
                    gos_ok = False
                effort = decision.effort
            efforts.append(effort)
            prompt = (
                f"[effort={effort}][verification_tier={verification_tier}] "
                f"{task['prompt']}\nReply with only the final answer."
            )
            calls += 1
            try:
                resp = provider.generate(
                    GenerateRequest(prompt=prompt, max_tokens=32, temperature=0.0)
                )
                ok = task["expect"].strip().upper() in resp.text.strip().upper()
                if ok:
                    successes += 1
                tokens += resp.input_tokens + resp.output_tokens
                latency += float(resp.latency_ms)
                cost += float(resp.cost_usd or 0.0)
            except ModelProviderError:
                failures += 1
        vuw = successes / len(task_set) if task_set else 0.0
        # Prefer token cost when USD is 0 (free tier)
        cost_units = cost if cost > 0 else max(tokens / 1000.0, 0.001)
        vuw_per_cost = round(vuw / cost_units, 6)
        trial_rows.append(
            {
                "policy": policy_name,
                "effort": fixed_effort or "/".join(efforts),
                "verified_useful_work": vuw,
                "successes": successes,
                "failures": failures,
                "model_calls": calls,
                "tokens": tokens,
                "latency_ms": latency,
                "cost_usd": cost,
                "cost_units": cost_units,
                "vuw_per_cost": vuw_per_cost,
                "verification_tier": verification_tier,
            }
        )

    best = max(trial_rows, key=lambda t: t["vuw_per_cost"])
    return {
        "hypothesis": "H-RSN-001",
        "fidelity": fidelity,
        "primary_metric": "VerifiedUsefulWork/Cost",
        "verification_requirement_fixed": verification_tier,
        "trials": trial_rows,
        "best_policy": best["policy"],
        "scientific_claim_accepted": False,
        "verdict": ("MEASURED_PROVIDER_OK_NOT_SCIENTIFIC" if gos_ok else "GOS_I23_VIOLATION"),
        "gos_i23_ok": gos_ok,
        "recorded_at": datetime.now(UTC).isoformat(),
        "limitations": (
            "Micro-task measured path; not long-horizon proof. "
            "Free-tier cost_units may use tokens when USD=0."
        ),
        "rule": "ReasoningBudget ≠ VerificationRequirement (GOS-I23)",
    }
