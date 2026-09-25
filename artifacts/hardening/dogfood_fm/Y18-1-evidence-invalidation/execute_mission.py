"""Y18-1 — Evidence change / invalidation (GOS-I12).

Hypothesis: After source invalidation, dependent claim→model→forecast→decision
chain becomes STALE/NEEDS_REVIEW; mission does not treat invalidated evidence as live.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
from global_os.evals.research.artifact_lock import (
    assert_artifact_path_writable,
    mission_artifact_dir,
)

from global_os.common.hashing import content_hash, new_id
from global_os.epistemic import EpistemicStore
from global_os.evals.research import PriorWorkReframe, run_research_mission
from global_os.runtime.events.ledger import EventLedger

ART = mission_artifact_dir(__file__)
assert_artifact_path_writable(ART / "mission.json")
def run_experiment() -> dict:
    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    goal_id = "goal_y18_1"
    ev = new_id("ev")
    cl = new_id("cl")
    mdl = new_id("mdl")
    fc = new_id("fc")
    dn = new_id("edn")
    digest = content_hash({"source": "ops_report_v1", "claim": "lead_time_90d"})
    epi.put_evidence(
        {
            "evidence_id": ev,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "EXTERNAL_UNTRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest,
        },
        tenant_id="dogfood",
        workspace_id="y18",
    )
    epi.put_claim(
        {
            "claim_id": cl,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "Lead time is 90 days",
            "status": "ACTIVE",
            "evidence_ids": [ev],
            "confidence": "MEDIUM",
            "confidence_basis": "single ops report",
            "recorded_at": now,
        },
        tenant_id="dogfood",
        workspace_id="y18",
    )
    epi.put_model(
        {
            "model_id": mdl,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "Lead-time planning model",
            "status": "ACTIVE",
            "depends_on_claim_ids": [cl],
            "recorded_at": now,
            "confidence": "MEDIUM",
            "confidence_basis": "ops",
        },
        tenant_id="dogfood",
        workspace_id="y18",
    )
    epi.put_forecast(
        {
            "forecast_id": fc,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "Ship by Q4",
            "status": "ACTIVE",
            "depends_on_model_ids": [mdl],
            "recorded_at": now,
            "horizon": "Q4",
        },
        tenant_id="dogfood",
        workspace_id="y18",
    )
    epi.put_decision(
        {
            "decision_id": dn,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "statement": "Commit inventory buffer",
            "status": "ACTIVE",
            "depends_on_forecast_ids": [fc],
            "depends_on_claim_ids": [cl],
            "options": ["buffer", "wait"],
            "chosen": "buffer",
            "recorded_at": now,
        },
        tenant_id="dogfood",
        workspace_id="y18",
    )
    # Mid-mission evidence change: source withdrawn
    inv = epi.invalidate_evidence(
        ev, tenant_id="dogfood", workspace_id="y18", reason="ops report retracted"
    )
    return {
        "failure_mode": "evidence_invalidation",
        "invalidation": inv,
        "claim_status": epi.get_claim(cl)["status"],
        "model_status": epi.get_model(mdl)["status"],
        "forecast_status": epi.get_forecast(fc)["status"],
        "decision_status": epi.get_decision(dn)["status"],
        "evidence_status": epi.get_evidence(ev)["status"],
        "event_types": sorted({e["event_type"] for e in ledger.list_events()}),
    }


def decide_fn(raw: dict) -> tuple[str, list[dict]]:
    ok = (
        raw["evidence_status"] == "INVALIDATED"
        and raw["claim_status"] == "STALE"
        and raw["model_status"] == "STALE"
        and raw["forecast_status"] == "STALE"
        and raw["decision_status"] == "NEEDS_REVIEW"
        and raw["invalidation"].get("claims")
        and raw["invalidation"].get("models")
        and raw["invalidation"].get("forecasts")
        and raw["invalidation"].get("decisions")
    )
    nulls: list[dict] = []
    if not ok:
        nulls.append({"id": "y18-1-propagation-miss", "detail": raw})
    return ("SUPPORTED" if ok else "REJECTED"), nulls


def verify(raw: dict) -> tuple[str, list[str]]:
    checks = [
        f"evidence={raw.get('evidence_status')}",
        f"claim={raw.get('claim_status')}",
        f"model={raw.get('model_status')}",
        f"forecast={raw.get('forecast_status')}",
        f"decision={raw.get('decision_status')}",
    ]
    ok = (
        raw.get("evidence_status") == "INVALIDATED"
        and raw.get("claim_status") == "STALE"
        and raw.get("decision_status") == "NEEDS_REVIEW"
    )
    return ("PASS" if ok else "FAIL"), checks


PREREG = {
    "mission_id": "Y18-1",
    "failure_mode_class": "evidence_change_invalidation",
    "primary_criterion": "GOS-I12 full chain after invalidate_evidence",
    "hypothesis": (
        "Invalidating accepted evidence marks claim STALE and propagates to "
        "model/forecast/decision (NEEDS_REVIEW)."
    ),
    "kill_criterion": "REJECTED if any downstream node stays ACTIVE after invalidation",
}


def main() -> None:
    report = run_research_mission(
        mission_id="Y18-1",
        artifact_root=ART,
        objective_text="Y18-1 dogfood: evidence invalidation propagates (GOS-I12)",
        hypothesis_statement=PREREG["hypothesis"],
        preregistration=PREREG,
        plan={"steps": ["seed chain", "invalidate evidence", "assert statuses"]},
        experiment_fn=run_experiment,
        decide_fn=decide_fn,
        deterministic_verify_fn=verify,
        kill_criteria=[PREREG["kill_criterion"]],
        alternative_explanations=["Graph incomplete", "Invalidation only marks evidence"],
        reopen_conditions=["Add assumption layer to chain"],
        reframe=PriorWorkReframe(
            discovered_prior_id="GOS-I12",
            original_intent="Scientific claim about lead times",
            reframed_intent="Dogfood Global OS invalidation invariant",
            rationale="Failure-mode diversity for freeze candidate",
        ),
        request_provider_iv=False,
        tenant_id="dogfood",
        workspace_id="y18",
    )
    print(report.decision, report.as_dict().get("verification"))


if __name__ == "__main__":
    main()
