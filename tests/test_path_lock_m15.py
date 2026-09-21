"""Path lock: incidents, DoD V2 gate, dogfooding (no new architecture)."""

from __future__ import annotations

import pytest

from global_os.evals.dogfood import DogfoodError, DogfoodMission, DogfoodStage
from global_os.evals.incident import IncidentStore
from global_os.evals.maturity.dod_v2 import DodStatus, summarize_dod_v2
from global_os.runtime.events.ledger import EventLedger


def test_incident_requires_postmortem_fields_and_events():
    ledger = EventLedger()
    store = IncidentStore(ledger)
    inc = store.record(
        title="OTLP collector volume permission denied",
        root_cause="otel-out directory not writable by collector user",
        blast_radius="CI Reality Contact OTLP live test",
        detection_gap="local docker worked; CI user mismatch unseen",
        why_tests_missed="accelerated path hid volume ownership",
        regression_test="tests/test_otlp_collector_live.py + compose user 0:0",
        fix="chmod 777 otel-out + user 0:0 in compose",
        residual_risk="shared volume still broad permissions",
        capability_ids=["otel_otlp_live_export"],
    )
    assert inc["incident_id"].startswith("inc_")
    assert inc["status"] == "OPEN"
    resolved = store.resolve(inc["incident_id"], status="RESOLVED")
    assert resolved["status"] == "RESOLVED"
    assert "resolved_at" in resolved
    types = {e["event_type"] for e in ledger.list_events()}
    assert "incident.recorded" in types
    assert "incident.resolved" in types


def test_dod_v2_not_closed_while_partials_exist():
    report = summarize_dod_v2()
    assert report["closed"] is False
    assert report["counts"][DodStatus.PARTIAL.value] >= 1
    ids = {i["id"] for i in report["items"]}
    assert "authority_non_bypass" in ids
    assert "maturity_from_evidence" in ids
    assert report["depends_on"] == "M1.5_OPERATIONALY_VALIDATED"


def test_dogfood_ordered_stages_and_no_autonomous_merge():
    ledger = EventLedger()
    mission = DogfoodMission(ledger)
    assert "trusted-core" in mission.MISSION.lower() or "trusted" in mission.MISSION.lower()
    p = mission.propose(
        proposal_id="df_1",
        title="Improve H-ENV live harness",
        rationale="need real-model ladder for M1.5",
        priority="P0",
        touches_trusted_core=False,
    )
    assert p["autonomous_merge_allowed"] is False
    assert p["stage"] == "propose"
    mission.advance("df_1", DogfoodStage.IMPLEMENT_BRANCH, branch_name="cursor/henv-live-2907")
    mission.advance("df_1", DogfoodStage.TEST)
    mission.advance("df_1", DogfoodStage.VERIFY)
    out = mission.advance("df_1", DogfoodStage.REQUEST_MERGE)
    assert out["stage"] == "request_merge"
    with pytest.raises(DogfoodError, match="autonomous merge forbidden"):
        mission.attempt_autonomous_merge("df_1")
    with pytest.raises(DogfoodError, match="in order"):
        mission.advance("df_1", DogfoodStage.OBSERVE)
    types = {e["event_type"] for e in ledger.list_events()}
    assert "dogfood.proposal_recorded" in types


def test_dogfood_trusted_core_still_cannot_self_merge():
    ledger = EventLedger()
    mission = DogfoodMission(ledger)
    mission.propose(
        proposal_id="df_t0",
        title="Touch Authority",
        rationale="experiment",
        priority="P1",
        touches_trusted_core=True,
    )
    with pytest.raises(DogfoodError, match="autonomous merge forbidden"):
        mission.attempt_autonomous_merge("df_t0")
