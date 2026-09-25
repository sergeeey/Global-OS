"""Execute Y19-H2 mechanistic follow-up (after H1 REJECTED)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING_H2,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H2,
    run_experiment_h2,
    write_preregistration_h2,
)

ART = Path(__file__).resolve().parent
METRICS = ART / "experiments" / "metrics"
write_preregistration_h2(ART / "preregistration.json")

PLAN = {
    "steps": [
        "Lock H2 prereg on new sealed seeds (disjoint from H1)",
        "Fit activity-only vs full baseline on TRAIN",
        "Compare sealed HOLD Brier ratio to MCID",
        "Decide; preserve nulls",
    ]
}


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h2()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"protocol={raw.get('protocol_version')}",
        f"disjoint_h1={raw.get('seed_policy', {}).get('disjoint_from_h1_and_y17')}",
        f"peek={raw.get('leak_checks', {}).get('peek_holdout_labels_in_train')}",
        f"ratio={raw.get('brier_ratio_full_over_activity')}",
        f"decision={raw.get('decision')}",
    ]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION_H2
        and raw.get("leak_checks", {}).get("peek_holdout_labels_in_train") is False
        and raw.get("answer_known_a_priori") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H2",
        artifact_root=ART,
        objective_text=(
            "Y19-H2: after H1 REJECTED, is baseline signal activity-core only, "
            "or do size/entropy extras improve sealed holdout by MCID?"
        ),
        hypothesis_statement=COMPETING_H2[0].statement,
        preregistration={
            "mission_id": "Y19-H2",
            "protocol_version": PROTOCOL_VERSION_H2,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H2[0].statement,
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "holdout_brier_ratio_full_over_activity",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {
                    "SUPPORTED": "ratio <= 0.90",
                    "REJECTED": "ratio > 0.90",
                    "INCONCLUSIVE": "balance fail",
                },
            },
        },
        plan=PLAN,
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=["holdout ratio > 0.90", "seed overlap with H1", "post-hoc MCID change"],
        alternative_explanations=[h.statement for h in COMPETING_H2[1:]],
        reopen_conditions=["non-linear activity features", "multi-IC per network"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H1",
            original_intent="Claim spectral early-warning",
            reframed_intent="Mechanistic decomposition of the winning baseline",
            rationale="H1 REJECTED honestly; next ask what the baseline actually uses",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
