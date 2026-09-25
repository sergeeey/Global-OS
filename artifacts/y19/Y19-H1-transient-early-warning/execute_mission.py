"""Execute Y19-H1 scientific dogfood mission via research orchestrator."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION,
    run_experiment,
    write_preregistration,
)

ART = Path(__file__).resolve().parent
METRICS = ART / "experiments" / "metrics"
PREREG_PATH = ART / "preregistration.json"
write_preregistration(PREREG_PATH)

PLAN = {
    "steps": [
        "Lock competing hypotheses + train/hold seeds + MCID before holdout decision",
        "Generate NK Boolean networks; extract early-window baseline vs candidate features",
        "Fit ridge linear probability on TRAIN only",
        "Evaluate sealed HOLD Brier + size ablation",
        "Decide SUPPORTED|REJECTED|INCONCLUSIVE; preserve nulls",
    ]
}


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"protocol={raw.get('protocol_version')}",
        f"train_hold_disjoint={raw.get('leak_checks', {}).get('train_hold_disjoint')}",
        f"peek={raw.get('leak_checks', {}).get('peek_holdout_labels_in_train')}",
        f"brier_ratio={raw.get('brier_ratio')}",
        f"decision={raw.get('decision')}",
        f"a_priori_unknown={raw.get('answer_known_a_priori') is False}",
    ]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION
        and raw.get("leak_checks", {}).get("train_hold_disjoint") is True
        and raw.get("leak_checks", {}).get("peek_holdout_labels_in_train") is False
        and raw.get("answer_known_a_priori") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
        and isinstance(raw.get("brier_ratio"), (int, float))
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H1",
        artifact_root=ART,
        objective_text=(
            "Y19-H1: do early spectral/sensitivity features predict long Boolean "
            "transients better than activity/entropy/size baselines on sealed holdout?"
        ),
        hypothesis_statement=COMPETING[0].statement,
        preregistration={
            "mission_id": "Y19-H1",
            "protocol_version": PROTOCOL_VERSION,
            "preregistered_before_data": True,
            "hypothesis": COMPETING[0].statement,
            "competing_hypotheses": [h.id for h in COMPETING],
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "holdout_brier_ratio",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {
                    "SUPPORTED": "ratio <= 0.90 AND ablated_ratio <= 0.90 AND holdout balance OK",
                    "REJECTED": "ratio > 0.90",
                    "INCONCLUSIVE": "balance fail OR MCID pass but ablation fail",
                },
            },
            "kill_criterion": (
                "SUPPORTED iff holdout Brier_candidate ≤ 0.90·baseline AND ablation OK; "
                "else REJECTED or INCONCLUSIVE per TZ"
            ),
        },
        plan=PLAN,
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=[
            "holdout brier_ratio > 0.90",
            "post-hoc MCID/tau/window change",
            "train/hold leakage",
        ],
        alternative_explanations=[h.statement for h in COMPETING[1:]],
        reopen_conditions=[
            "new sealed holdout family (different N/K prior)",
            "stronger non-linear candidate class with new preregistration",
        ],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y17-3+Y17-5",
            original_intent="Repeat Boolean clamp or RMT ω-forecast",
            reframed_intent=(
                "New early-warning question on generated NK nets with sealed holdout"
            ),
            rationale="Dogfood unknown-answer science; not confirmatory replay",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
