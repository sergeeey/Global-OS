"""Execute Y17-5 forecasting mission via research orchestrator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from global_os.evals.research.artifact_lock import (
    assert_artifact_path_writable,
    mission_artifact_dir,
)

from global_os.evals.research import PriorWorkReframe, run_research_mission

ART = mission_artifact_dir(__file__)
assert_artifact_path_writable(ART / "mission.json")
EXP = ART / "experiments"
spec = importlib.util.spec_from_file_location("y17_5_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-5",
    "preregistered_before_data": True,
    "hypothesis": (
        "An OLS forecast log(M1)~a+b·ω(A), fit only on TRAIN seeds 550-564 (N_DIM=24), "
        "achieves holdout RMSE ≤ 0.90× the TRAIN-mean baseline on HOLD seeds 650-664."
    ),
    "primary_outcome": "holdout RMSE_model / RMSE_baseline",
    "test": "seed holdout forecasting; competing mean baseline",
    "null": "model fails MCID (ratio > 0.90) on holdout",
    "alpha": "MCID_RATIO=0.90 (not a p-value)",
    "threshold": {"mcid_ratio": 0.90},
    "kill_criterion": (
        "SUPPORTED iff holdout RMSE_model ≤ 0.90·RMSE_baseline; else REJECTED. "
        "No refit on holdout; no post-hoc MCID change."
    ),
    "seed_data_policy": (
        "TRAIN 550-564; HOLD 650-664; disjoint from each other and from Y17-1/Y17-4 ranges."
    ),
    "stopping_rule": "Single locked split; one fit; one holdout evaluation.",
    "prohibited_post_hoc_changes": [
        "Do not peek holdout before locking model",
        "Do not change MCID after seeing ratio",
        "Do not switch feature from ω to κ/K after holdout",
        "Do not merge train+hold for final fit",
        "training information ≠ future/holdout information",
    ],
    "primary_criterion": {
        "statistic": "holdout_rmse_ratio",
        "mcid_ratio": 0.90,
        "decision_rule": {
            "SUPPORTED": "ratio <= 0.90",
            "REJECTED": "ratio > 0.90",
        },
    },
    "secondary_descriptive_only": ["train RMSE", "slope/intercept", "in-sample vs holdout gap"],
}

PLAN = {
    "steps": [
        "Lock train/hold seeds and MCID before any holdout compute",
        "Collect TRAIN (ω, M1); fit OLS; record baseline mean(log M1)",
        "Collect HOLD; evaluate RMSEs; decide",
        "Deterministic verify leak checks; provider IV degraded if blocked",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-5",
        artifact_root=ART,
        objective_text=(
            "Y17-5 dogfood: forecasting with locked seed holdout — must ω(A) OLS "
            "beat mean baseline on future seeds?"
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "ω–M1 association is sample-specific (fails transport to new seeds)",
            "Mean baseline already near irreducible error at N_DIM=24",
            "Nonlinear / interaction model needed (out of scope)",
        ],
        reopen_conditions=[
            "Larger N_DIM holdout with same protocol",
            "Multi-feature model with nested holdout still beating baseline",
        ],
        sources={
            "y17_multin": str(mod.MULTIN),
            "y17_dim": str(mod.DIM),
            "y17_abs": str(mod.ABS),
            "protocol_note": "training information ≠ future information",
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="H-B2-1n/Y17-1",
            original_intent="confirmatory correlation of ω(A) with M1 (Fisher)",
            reframed_intent="predictive holdout test: does fitted ω→M1 beat mean baseline?",
            rationale=(
                "Correlation support ≠ forecasting skill. Y17-5 asks the predictive question "
                "with locked holdout and competing baseline — different class from Y17-1."
            ),
        ),
        request_provider_iv=True,
    )
    print(
        {
            "mission_id": report.mission_id,
            "decision": report.decision,
            "provider_iv": report.verification.provider_status,
            "failure_cases": report.failure_cases,
        }
    )


if __name__ == "__main__":
    main()
