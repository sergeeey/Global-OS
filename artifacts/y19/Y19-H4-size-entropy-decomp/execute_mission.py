"""Execute Y19-H4 size vs entropy decomposition."""

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
    COMPETING_H4,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H4,
    run_experiment_h4,
    write_preregistration_h4,
)

ART = mission_artifact_dir(__file__)
assert_artifact_path_writable(ART / "mission.json")
METRICS = ART / "experiments" / "metrics"
write_preregistration_h4(ART / "preregistration.json")

PLAN = {
    "steps": [
        "Lock H4 decomposition gates (no new feature families)",
        "Gate A: N-matched activity+entropy vs activity",
        "Gate B: residualized entropy + nested N control",
        "Gate C: leave-one-N-out transfer of entropy effect",
        "Decide; preserve nulls; do not overclaim",
    ]
}


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h4()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    gates = raw.get("gates") or {}
    checks = [
        f"protocol={raw.get('protocol_version')}",
        f"A={gates.get('A_n_matched', {}).get('status')}",
        f"B={gates.get('B_residualized_entropy', {}).get('status')}",
        f"C={gates.get('C_leave_one_n_out', {}).get('status')}",
        f"decision={raw.get('decision')}",
    ]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION_H4
        and raw.get("answer_known_a_priori") is False
        and raw.get("leak_checks", {}).get("peek_holdout_labels_in_train") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
        and set(gates) >= {"A_n_matched", "B_residualized_entropy", "C_leave_one_n_out"}
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H4",
        artifact_root=ART,
        objective_text=(
            "Y19-H4: after H3, does entropy survive N control, or is the effect mostly size?"
        ),
        hypothesis_statement=COMPETING_H4[0].statement,
        preregistration={
            "mission_id": "Y19-H4",
            "protocol_version": PROTOCOL_VERSION_H4,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H4[0].statement,
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "all_three_decomposition_gates_pass",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {
                    "SUPPORTED": "A and B and C PASS",
                    "REJECTED": "A or B FAIL",
                    "INCONCLUSIVE": "mixed or UNDERPOWERED",
                },
            },
        },
        plan=PLAN,
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=["A/B FAIL under N control", "new spectral features", "post-hoc MCID"],
        alternative_explanations=[h.statement for h in COMPETING_H4[1:]],
        reopen_conditions=["interaction N×entropy model with new prereg", "larger N panel"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H3",
            original_intent="Treat size/entropy combo as entropy predicts transients",
            reframed_intent="Decompose whether entropy survives N control",
            rationale="H3 strengthens combo evidence; carrier identity still open",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
