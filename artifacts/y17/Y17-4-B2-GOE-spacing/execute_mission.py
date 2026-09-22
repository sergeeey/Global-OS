"""Execute Y17-4 through Global OS research mission orchestrator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission

ART = Path(__file__).resolve().parent
EXP = ART / "experiments"
sys.path.insert(0, str(EXP))

spec = importlib.util.spec_from_file_location("y17_4_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-4",
    "preregistered_before_data": True,
    "hypothesis": (
        "Nearest-neighbor spacing ratios ⟨r⟩ of eigenvalues of the symmetric part "
        "(A+Aᵀ)/2 for the B2 Chernoff/Neural-ODE matrix family (N_DIM=32, seeds 500-519) "
        "are GOE-like: within TOL=0.05 of the GOE surmise and closer to GOE than Poisson."
    ),
    "primary_outcome": "mean ⟨r⟩ across 20 matrices vs GOE/Poisson/GUE surmises",
    "test": "eigvalsh((A+A.T)/2) → r-stat; synthetic GOE/Poisson controls",
    "null": "⟨r⟩ outside GOE band OR closer to Poisson OR controls fail",
    "alpha": "deterministic band TOL=0.05 (not p-value)",
    "threshold": {"tol": 0.05, "target": "GOE_surmise_0.535898"},
    "kill_criterion": (
        "SUPPORTED iff GOE+Poisson controls OK AND |⟨r⟩-R_GOE|<0.05 AND "
        "dist(GOE)<dist(Poisson). Else REJECTED."
    ),
    "seed_data_policy": (
        "Fresh seeds 500-519; disjoint from Y17-1 (400-459). "
        "Read-only Y-17 multin builder. No Odlyzko download required."
    ),
    "stopping_rule": "Single locked sweep; no post-hoc TOL or seed changes.",
    "prohibited_post_hoc_changes": [
        "Do not widen TOL after seeing r_bar",
        "Do not switch primary target to GUE after data",
        "Do not claim P-RIEMANN-RMT resolved",
        "Do not write into Y-17",
    ],
    "primary_criterion": {
        "statistic": "r_bar_vs_GOE_band",
        "tol": 0.05,
        "decision_rule": {
            "SUPPORTED": "controls OK AND in_goe_band AND closer_to_goe_than_poisson",
            "REJECTED": "otherwise",
        },
    },
    "secondary_descriptive_only": ["distance to GUE", "per-seed r", "control means"],
}

PLAN = {
    "steps": [
        "Lock prereg for cross-domain GOE-spacing probe",
        "Run synthetic GOE/Poisson controls",
        "Build 20 B2 matrices (seeds 500-519), compute ⟨r⟩ on symmetric-part spectra",
        "Decide vs locked band; provider IV degraded if blocked",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-4",
        artifact_root=ART,
        objective_text=(
            "Y17-4 dogfood: cross-domain RMT probe — are B2 symmetric-part spectra "
            "GOE-like under nearest-neighbor spacing ratios?"
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "Strong diagonal structure forces near-Poisson spacings",
            "Finite-N=32 artifact; larger N would recover GOE",
            "Ginibre/non-Hermitian statistics more appropriate for A itself (not tested)",
        ],
        reopen_conditions=[
            "Larger N_DIM sweep with locked TOL",
            "Compare eig(A) complex spacings to Ginibre",
            "Local-keys provider IV of this decision",
        ],
        sources={
            "y17_multin": str(mod.MULTIN),
            "open_parent": "P-RIEMANN-RMT",
            "r_stat_refs": "Atas et al. PRL 110, 084101 (2013); H-B1-1a pipeline",
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="P-RIEMANN-RMT",
            original_intent="resolve spectral universality for non-number-theoretic spectra",
            reframed_intent=(
                "bounded probe: GOE-likeness of one structured engineering matrix family "
                "(B2), not full universality claim"
            ),
            rationale=(
                "P-RIEMANN-RMT is open and broad. Y17-4 tests research-runner generality on "
                "a cross-domain RMT class with local compute and null-capable band criterion."
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
