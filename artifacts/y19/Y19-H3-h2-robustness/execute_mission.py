"""Execute Y19-H3 robustness mission (H2 stress test)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING_H3,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H3,
    run_experiment_h3,
    write_preregistration_h3,
)

ART = Path(__file__).resolve().parent
METRICS = ART / "experiments" / "metrics"
write_preregistration_h3(ART / "preregistration.json")

PLAN = {
    "steps": [
        "Lock three robustness gates before holdout scoring",
        "Gate A: activity-tertile matched full vs activity",
        "Gate B: unseen N=24 hold after train N∈{16,20}",
        "Gate C: K=2 and K=3 regime slices",
        "Aggregate SUPPORTED|REJECTED|INCONCLUSIVE; preserve nulls",
    ]
}


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h3()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    gates = raw.get("gates") or {}
    checks = [
        f"protocol={raw.get('protocol_version')}",
        f"A={gates.get('A_activity_matched', {}).get('status')}",
        f"B={gates.get('B_unseen_size', {}).get('status')}",
        f"C={gates.get('C_regime_k', {}).get('status')}",
        f"decision={raw.get('decision')}",
        f"a_priori_unknown={raw.get('answer_known_a_priori') is False}",
    ]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION_H3
        and raw.get("leak_checks", {}).get("peek_holdout_labels_in_train") is False
        and raw.get("answer_known_a_priori") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
        and set(gates) >= {"A_activity_matched", "B_unseen_size", "C_regime_k"}
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H3",
        artifact_root=ART,
        objective_text=(
            "Y19-H3: does H2 size/entropy gain survive activity matching, "
            "unseen system size, and both K regimes?"
        ),
        hypothesis_statement=COMPETING_H3[0].statement,
        preregistration={
            "mission_id": "Y19-H3",
            "protocol_version": PROTOCOL_VERSION_H3,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H3[0].statement,
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "all_three_gates_pass",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {
                    "SUPPORTED": "A and B and C PASS",
                    "REJECTED": "any gate FAIL",
                    "INCONCLUSIVE": "any UNDERPOWERED and none FAIL",
                },
            },
        },
        plan=PLAN,
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=[
            "any robustness gate FAIL",
            "seed overlap with H1/H2",
            "post-hoc MCID/gate rewrite",
        ],
        alternative_explanations=[h.statement for h in COMPETING_H3[1:]],
        reopen_conditions=[
            "larger unseen-N panel (N=28+)",
            "explicit N-matched entropy residualization",
        ],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H2",
            original_intent="Treat H2 size/entropy gain as settled",
            reframed_intent="Stress-test H2 under matching, transfer, and regime splits",
            rationale="H2 SUPPORTED is necessary but not sufficient for structural claim",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
