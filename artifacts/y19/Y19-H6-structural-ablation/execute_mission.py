"""Execute Y19-H6 structural ablation — autonomous campaign step."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.evals.research.y19_transient_early_warning import (
    COMPETING_H6,
    MCID_BRIER_RATIO,
    PROTOCOL_VERSION_H6,
    run_experiment_h6,
    write_preregistration_h6,
)

ART = Path(__file__).resolve().parent
METRICS = ART / "experiments" / "metrics"
write_preregistration_h6(ART / "preregistration.json")


def experiment_fn() -> dict[str, Any]:
    raw = run_experiment_h6()
    METRICS.mkdir(parents=True, exist_ok=True)
    (METRICS / "run.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return raw


def _decide(raw: dict) -> tuple[str, list[dict]]:
    return raw["decision"], list(raw.get("null_results") or [])


def _verify(raw: dict) -> tuple[str, list[str]]:
    gates = raw.get("gates") or {}
    checks = [f"protocol={raw.get('protocol_version')}", f"decision={raw.get('decision')}"]
    ok = (
        raw.get("protocol_version") == PROTOCOL_VERSION_H6
        and raw.get("answer_known_a_priori") is False
        and raw.get("decision") in {"SUPPORTED", "REJECTED", "INCONCLUSIVE"}
        and len(gates) >= 4
    )
    return ("PASS" if ok else "FAIL"), checks


def main() -> None:
    report = run_research_mission(
        mission_id="Y19-H6",
        artifact_root=ART,
        objective_text="Y19-H6: ablate H5b structural probes — propensity vs period structure",
        hypothesis_statement=COMPETING_H6[0].statement,
        preregistration={
            "mission_id": "Y19-H6",
            "protocol_version": PROTOCOL_VERSION_H6,
            "preregistered_before_data": True,
            "hypothesis": COMPETING_H6[0].statement,
            "mcid_brier_ratio": MCID_BRIER_RATIO,
            "primary_criterion": {
                "statistic": "h6_structural_ablation",
                "mcid_ratio": MCID_BRIER_RATIO,
                "decision_rule": {"SUPPORTED": "triage H6a or H6b", "INCONCLUSIVE": "mixed"},
            },
        },
        plan={"steps": ["ablate mean transient vs period set", "decide", "update campaign state"]},
        experiment_fn=experiment_fn,
        decide_fn=_decide,
        deterministic_verify_fn=_verify,
        kill_criteria=["label leak", "post-hoc MCID"],
        alternative_explanations=[h.statement for h in COMPETING_H6[1:]],
        reopen_conditions=["transfer of propensity across N", "analytic NK transient theory"],
        reframe=PriorWorkReframe(
            discovered_prior_id="Y19-H5",
            original_intent="Stop after H5b",
            reframed_intent="Continue campaign: which structural feature carries the win",
            rationale="Y19-RESEARCH-PROGRAM: closed H is checkpoint not halt",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y19",
    )
    print(report.decision, report.verification.deterministic_status)
    raise SystemExit(0 if report.verification.deterministic_status == "PASS" else 1)


if __name__ == "__main__":
    main()
