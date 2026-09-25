"""Execute Y17-2 through Global OS research mission orchestrator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]  # /workspace
sys.path.insert(0, str(ROOT / "src"))
from global_os.evals.research.artifact_lock import (
    assert_artifact_path_writable,
    mission_artifact_dir,
)

from global_os.evals.research import PriorWorkReframe, run_research_mission

ART = mission_artifact_dir(__file__)
assert_artifact_path_writable(ART / "mission.json")
EXP = ART / "experiments"
sys.path.insert(0, str(EXP))

spec = importlib.util.spec_from_file_location("y17_2_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-2",
    "preregistered_before_data": True,
    "hypothesis": (
        "On H-CAT31-3 committed composite rows, nested weighted F-test prefers "
        "Var(n)=C/n+D/n² over Var(n)=C/n at α=0.05 with D>0 "
        "(H-CAT31-4 Relaxation Map V3)."
    ),
    "primary_outcome": "nested_F p-value and sign of D_hat",
    "test": "weighted nested F-test (M1 vs M0), α=0.05",
    "null": "M0 Var=C/n is adequate (extra D/n² not justified)",
    "alpha": 0.05,
    "threshold": {"p_F": 0.05, "D_sign": "positive"},
    "kill_criterion": (
        "REJECTED if nested F p>=0.05 OR (p<0.05 and D_hat<=0). "
        "Do not upgrade using prime secondary rows."
    ),
    "seed_data_policy": (
        "READ-ONLY reuse of committed Y-17 metrics (no fresh LP seeds). "
        "Primary=H-CAT31-3 composite; secondary=H-CAT31-4 primes walled off."
    ),
    "stopping_rule": "Single locked analysis on pre-declared rows; no iterative model shopping.",
    "prohibited_post_hoc_changes": [
        "Do not change α after seeing p",
        "Do not switch primary population to primes after composite fails",
        "Do not replace nested F with R² beauty contest",
        "Do not claim asymptotic proof of C/n+D/n² law",
    ],
    "primary_criterion": {
        "statistic": "nested_F_p_and_D_sign",
        "alpha": 0.05,
        "decision_rule": {
            "SUPPORTED": "p_F < 0.05 AND D_hat > 0",
            "REJECTED": "otherwise",
        },
    },
    "secondary_descriptive_only": [
        "prime nested F",
        "delta AIC",
        "secondary agreement flag",
    ],
}

PLAN = {
    "steps": [
        "PriorWorkReframe: abandon closed H-B7-2/3 transient Rb",
        "Lock preregistration for H-CAT31 V3 nested models",
        "Load committed composite + prime Var rows (read-only)",
        "Fit M0 and M1 with inverse-variance weights",
        "Nested F-test → decision",
        "Deterministic verification; provider IV if available else BLOCKED_ENVIRONMENT",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-2",
        artifact_root=ART,
        objective_text=(
            "Y17-2 dogfood: test H-CAT31-4 Relaxation Map V3 — does nested model "
            "comparison prefer C/n+D/n² over C/n on committed Lovász variance rows?"
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "Pure power-law Var∝n^b with b≠-1 (already REJECTED-as-exact-minus-1 by H-CAT31-3)",
            "Slowly varying L(n) in C/n·L(n) not capturable by D/n² on this n-range",
            "Weighting / SE misspecification dominates nested F",
        ],
        reopen_conditions=[
            "Fresh independent LP seeds at matched n for both arithmetic classes",
            "Pre-registered joint prime+composite common-slope design (H-CAT31-4 V2)",
        ],
        sources={
            "y17_composite": str(mod.COMPOSITE_RUN),
            "y17_primes": str(mod.PRIME_ANALYSIS),
            "named_next_step": "H-CAT31-4 decision.md Relaxation Map V3",
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="H-B7-3",
            original_intent="Y17-2 transient Rb after permanent clamp (H-B7-2 Relaxation Map)",
            reframed_intent="H-CAT31-4 Relaxation Map V3 nested Var model comparison",
            rationale=(
                "H-B7-2 permanent clamp and H-B7-3 transient Rb already CLOSED in Y-17 "
                "(H-B7-3 TASK_INFEASIBLE for strict Kauffman test in Fauré model). "
                "Per mission criteria: choose another unfinished hypothesis, different "
                "class from Y17-1 Fisher confirmatory. V3 is named unfinished next step "
                "with local committed materials and null-capable nested F-test."
            ),
        ),
        request_provider_iv=True,
    )
    print(
        {
            "mission_id": report.mission_id,
            "decision": report.decision,
            "provider_iv": report.verification.provider_status,
            "artifact_root": report.artifact_root,
            "failure_cases": report.failure_cases,
        }
    )


if __name__ == "__main__":
    main()
