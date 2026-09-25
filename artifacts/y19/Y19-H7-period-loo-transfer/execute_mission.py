"""Execute Y19-H7 leave-one-N-out period transfer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from global_os.evals.research.artifact_lock import (
    assert_artifact_path_writable,
    mission_artifact_dir,
)

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING_H7,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H7,
    run_experiment_h7,
)

ART = mission_artifact_dir(__file__)
assert_artifact_path_writable(ART / "mission.json")
METRICS = ART / "experiments" / "metrics"


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h7()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    (ART / "preregistration.json").write_text(
        json.dumps(
            {
                "mission_id": "Y19-H7",
                "protocol_version": PROTOCOL_VERSION_H7,
                "preregistered_before_data": True,
                "hypothesis": COMPETING_H7[0].statement,
                "primary_criterion": {
                    "statistic": "loo_period_vs_n",
                    "mcid_ratio": MCID_BRIER_RATIO,
                    "decision_rule": {
                        "SUPPORTED": "≥2 LOO folds PASS",
                        "REJECTED": "powered folds fail MCID",
                    },
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return raw


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H7",
        artifact_root=ART,
        objective_text="Y19-H7: does period structure transfer leave-one-N-out vs raw N?",
        hypothesis_statement=COMPETING_H7[0].statement,
        preregistration={
            "mission_id": "Y19-H7",
            "protocol_version": PROTOCOL_VERSION_H7,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H7[0].statement,
            "primary_criterion": {
                "statistic": "loo_period_vs_n",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {"SUPPORTED": "≥2 folds", "REJECTED": "fail"},
            },
        },
        plan={"steps": ["LOO period vs N", "decide", "update campaign"]},
        experiment_fn=experiment_fn,
        decide_fn=lambda raw: (raw["decision"], list(raw.get("null_results") or [])),
        deterministic_verify_fn=lambda raw: (
            (
                "PASS"
                if raw.get("protocol_version") == PROTOCOL_VERSION_H7
                and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
                else "FAIL"
            ),
            [f"decision={raw.get('decision')}"],
        ),
        kill_criteria=["post-hoc MCID"],
        alternative_explanations=[h.statement for h in COMPETING_H7[1:]],
        reopen_conditions=["analytic theory", "new system family"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H6",
            original_intent="Stop after H6b",
            reframed_intent="Test transfer of period structure across N",
            rationale="Campaign continues until terminal claim or low EVI",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
