"""Execute Y19-H5 (why N) — autonomous campaign step."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING_H5,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H5,
    run_experiment_h5,
    write_preregistration_h5,
)

ART = Path(__file__).resolve().parent
METRICS = ART / "experiments" / "metrics"
write_preregistration_h5(ART / "preregistration.json")

PLAN = {
    "steps": [
        "Lock H5a/H5b/H5d prereg; sealed seeds disjoint from H1–H4",
        "Probe basin/cycle stats (non-labeled ICs) vs n / log2_n",
        "N-matched structural vs activity",
        "Protocol ablation under alt τ",
        "Triage mechanism; update campaign durable state",
    ]
}


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h5()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    gates = raw.get("gates") or {}
    checks = [
        f"protocol={raw.get('protocol_version')}",
        f"A={gates.get('A_structural_vs_n', {}).get('status')}",
        f"B={gates.get('B_n_matched_structural', {}).get('status')}",
        f"C={gates.get('C_protocol_ablation', {}).get('status')}",
        f"winner={raw.get('winning_hypothesis_id')}",
        f"no_label_leak={raw.get('leak_checks', {}).get('structural_uses_labeled_ic_outcome') is False}",
    ]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION_H5
        and raw.get("answer_known_a_priori") is False
        and raw.get("leak_checks", {}).get("peek_holdout_labels_in_train") is False
        and raw.get("leak_checks", {}).get("structural_uses_labeled_ic_outcome") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
        and set(gates) >= {
            "A_structural_vs_n",
            "B_n_matched_structural",
            "C_protocol_ablation",
        }
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H5",
        artifact_root=ART,
        objective_text=(
            "Y19-H5 campaign step: why does N predict long-transient labels — "
            "state-space vs basin/cycle structure vs protocol artifact?"
        ),
        hypothesis_statement=COMPETING_H5[0].statement,
        preregistration={
            "mission_id": "Y19-H5",
            "protocol_version": PROTOCOL_VERSION_H5,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H5[0].statement,
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "h5_mechanism_triage",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {
                    "SUPPORTED": "mechanism triage selects H5a or H5b or H5d with powered gates",
                    "INCONCLUSIVE": "mixed or underpowered",
                    "REJECTED": "unused for H5 triage (prefer INCONCLUSIVE over false REJECTED)",
                },
            },
        },
        plan=PLAN,
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=["label leak via labeled IC transient feature", "post-hoc MCID", "seed overlap"],
        alternative_explanations=[h.statement for h in COMPETING_H5[1:]],
        reopen_conditions=["H5c explicit proxy search", "multi-IC label definition"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H4",
            original_intent="Ask operator whether to study why N",
            reframed_intent="Autonomous campaign step: triage mechanisms for N→label",
            rationale="Y19-RESEARCH-PROGRAM forbids dispatcher stops after closed Hx",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status, flush=True)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
