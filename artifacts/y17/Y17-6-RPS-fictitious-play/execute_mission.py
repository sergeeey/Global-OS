"""Execute Y17-6 RPS fictitious-play mission via research orchestrator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission

ART = Path(__file__).resolve().parent
EXP = ART / "experiments"
spec = importlib.util.spec_from_file_location("y17_6_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-6",
    "preregistered_before_data": True,
    "hypothesis": (
        "On rock-paper-scissors zero-sum, fictitious play (T=400, 40 seeds) achieves "
        "mean exploitability ≤ 0.25× an always-Rock pure baseline."
    ),
    "primary_outcome": "mean_exploit_fp / mean_exploit_pure",
    "test": "fictitious play vs pure-strategy baseline",
    "null": "FP fails MCID (ratio > 0.25)",
    "alpha": "MCID_RATIO=0.25",
    "threshold": {"mcid_ratio": 0.25},
    "kill_criterion": (
        "SUPPORTED iff mean_exploit(FP) ≤ 0.25·mean_exploit(PURE_ROCK); else REJECTED."
    ),
    "seed_data_policy": "Seeds 700-739; no Y-17 writes.",
    "stopping_rule": "Single locked ensemble; no post-hoc MCID change.",
    "prohibited_post_hoc_changes": [
        "Do not switch baseline to uniform-Nash after seeing results",
        "Do not claim open-problem #13 solved",
        "Do not write into Y-17",
    ],
    "primary_criterion": {
        "statistic": "exploit_ratio_fp_over_pure",
        "mcid_ratio": 0.25,
        "decision_rule": {"SUPPORTED": "ratio <= 0.25", "REJECTED": "ratio > 0.25"},
    },
    "secondary_descriptive_only": ["distance to Nash", "per-seed mixes"],
}

PLAN = {
    "steps": [
        "Lock RPS payoff, T, seeds, MCID, pure baseline",
        "Run FP vs PURE exploitability ensemble",
        "Decide vs MCID; persist null/contradictory",
        "Deterministic verify",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-6",
        artifact_root=ART,
        objective_text=(
            "Y17-6 dogfood: game-theoretic probe — does fictitious play beat "
            "a pure-strategy baseline on RPS exploitability?"
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "Exploitability metric too weak for learning claim",
            "Always-Rock baseline is strawman (still valid MCID comparison)",
            "Finite-T FP oscillates without converging in exploit",
        ],
        reopen_conditions=[
            "Matching-pennies / general-sum games with same protocol",
            "Instance-dependent sample complexity bound checks",
        ],
        sources={
            "catalog_bridge": "Y-17 open-problem #13 Nash zero-sum (probe only)",
            "payoff": "RPS 3x3",
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="catalog:#13-nash-zero-sum",
            original_intent="Instance-dependent Nash sample complexity (full open problem)",
            reframed_intent="Finite-T FP vs pure baseline exploitability on RPS",
            rationale="Full #13 is open; this is a computable dogfood probe of learning dynamics",
        ),
        request_provider_iv=False,
    )
    print(
        {
            "mission_id": report.mission_id,
            "decision": report.decision,
            "verification": report.verification.as_dict(),
        }
    )


if __name__ == "__main__":
    main()
