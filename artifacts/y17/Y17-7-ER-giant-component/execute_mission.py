"""Execute Y17-7 ER giant-component mission via research orchestrator."""

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
spec = importlib.util.spec_from_file_location("y17_7_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-7",
    "preregistered_before_data": True,
    "hypothesis": (
        "For Erdős–Rényi G(n=200,p), the empirical p50 where Prob(|LCC|/n≥0.5)=0.5 "
        "lies within relative error 0.35 of the theoretical threshold p_c=1/n."
    ),
    "primary_outcome": "|p50 - 1/n| / (1/n)",
    "test": "ER giant-component threshold scan",
    "null": "rel_err > 0.35",
    "alpha": "REL_TOL=0.35",
    "threshold": {"rel_tol": 0.35, "n": 200},
    "kill_criterion": "SUPPORTED iff rel_err ≤ 0.35; else REJECTED.",
    "seed_data_policy": "Seeds from 800; 60 graphs per p-factor; no Y-17 writes.",
    "stopping_rule": "Single locked grid; no post-hoc TOL/N change.",
    "prohibited_post_hoc_changes": [
        "Do not widen REL_TOL after seeing p50",
        "Do not switch giant definition after data",
        "Do not write into Y-17",
    ],
    "primary_criterion": {
        "statistic": "rel_err_p50_vs_pc",
        "rel_tol": 0.35,
        "decision_rule": {"SUPPORTED": "rel_err <= 0.35", "REJECTED": "rel_err > 0.35"},
    },
    "secondary_descriptive_only": ["giant rates per factor", "mean LCC frac"],
}

PLAN = {
    "steps": [
        "Lock N, p-grid factors, giant frac, REL_TOL",
        "Sweep ER graphs; estimate p50 by interpolation",
        "Decide vs band; persist null/contradictory",
        "Deterministic verify monotonicity soft check",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-7",
        artifact_root=ART,
        objective_text=(
            "Y17-7 dogfood: network phase-transition probe — is ER giant-component "
            "p50 near 1/n for finite n=200?"
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "Finite-size shift of critical window (n^{2/3} scaling)",
            "Giant definition |LCC|/n≥0.5 too late vs continuum onset",
            "Interpolation artifacts on coarse p-grid",
        ],
        reopen_conditions=[
            "Larger N with same protocol",
            "Susceptibility peak location vs p_c",
        ],
        sources={
            "model": "Erdős–Rényi G(n,p)",
            "theory": "p_c = 1/n giant-component threshold",
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="catalog:network-phase-transition",
            original_intent="Rigorous Markov-switching nonlinear network theory",
            reframed_intent="Finite-n ER giant-component p50 vs 1/n band check",
            rationale=(
                "Full nonlinear switching theory is open; ER threshold is a clean "
                "network dogfood probe"
            ),
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
