"""Execute Y17-3 through Global OS research mission orchestrator."""

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
sys.path.insert(0, str(EXP))

spec = importlib.util.spec_from_file_location("y17_3_run", EXP / "run_mission.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PREREG = {
    "mission_id": "Y17-3",
    "preregistered_before_data": True,
    "hypothesis": (
        "Permanent do(Rb=0) on the Fauré 2006 network makes the CycD=0 region reach a "
        "complex attractor (operationalized Kauffman permanent-clamp claim)."
    ),
    "primary_outcome": "cycd0_reaches_complex_attractor under do(Rb=0)",
    "test": "exhaustive synchronous attractor membership under clamped Boolean rules",
    "null": "all CycD=0 states still reach only point attractor(s) under do(Rb=0)",
    "alpha": "deterministic exhaustive (no α); binary complex-vs-point",
    "threshold": {"complex_in_cycd0": True},
    "kill_criterion": (
        "SUPPORTED if do(Rb=0) yields complex attractor from CycD=0; "
        "REJECTED otherwise. do(p27=0) is secondary differential only."
    ),
    "seed_data_policy": (
        "Deterministic exhaustive enumeration; no RNG. Read-only import of Y-17 H-B7-1/2 helpers."
    ),
    "stopping_rule": "Single exhaustive run; no post-hoc node/clamp changes.",
    "prohibited_post_hoc_changes": [
        "Do not switch to transient clamp after seeing permanent result",
        "Do not rewrite Y-17 metrics",
        "Do not claim pre-existing wild-type attractor without separate test",
        "Do not upgrade p27 secondary into primary",
    ],
    "primary_criterion": {
        "statistic": "cycd0_reaches_complex_attractor",
        "decision_rule": {
            "SUPPORTED": "True under do(Rb=0)",
            "REJECTED": "False under do(Rb=0)",
        },
    },
    "secondary_descriptive_only": [
        "do(p27=0) types",
        "match to H-B7-2 committed metrics",
        "complex period",
    ],
}

PLAN = {
    "steps": [
        "PriorWorkReframe: independent verification of H-B7-2 (not first discovery)",
        "Lock preregistration for permanent-clamp Rb primary",
        "Import H-B7-1/2 helpers read-only",
        "Exhaustive do(Rb=0) and do(p27=0)",
        "Decide + deterministic verify; provider IV degraded if blocked",
    ]
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y17-3",
        artifact_root=ART,
        objective_text=(
            "Y17-3 dogfood: independent causal recompute of H-B7-2 permanent clamps "
            "to exercise research runner on Boolean do-operator class."
        ),
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan=PLAN,
        experiment_fn=mod.run_experiment,
        decide_fn=mod.decide_fn,
        deterministic_verify_fn=mod.deterministic_verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=[
            "Bug in clamp_rule / attractor membership",
            "Node-order mismatch vs H-B7-1",
            "Transient (not permanent) clamp would be required for strict Kauffman claim",
        ],
        reopen_conditions=[
            "Different Boolean network with multi-attractor CycD=0 region",
            "Async update scheme pre-registered separately",
        ],
        sources={
            "y17_h1": str(mod.H1),
            "y17_h2": str(mod.H2),
            "prior_metrics": str(mod.H2_PRIOR_METRICS),
        },
        reframe=PriorWorkReframe(
            discovered_prior_id="H-B7-2",
            original_intent="first discovery of permanent-clamp Rb effect",
            reframed_intent="independent Global-OS recompute / verification of H-B7-2 Rb arm",
            rationale=(
                "H-B7-2 already CONFIRMED[WEAKENED] in Y-17. Y17-3 tests research-runner "
                "generality on a causal Boolean class distinct from Y17-1/Y17-2, with explicit "
                "independent-verification framing (not silent rediscovery)."
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
