"""P2: CLI time-travel replay over ledger (ADR-0013)."""

from __future__ import annotations

from global_os.cli import main
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.events.replay import EventReplayEngine


def test_replay_until_index_and_compare() -> None:
    ledger = EventLedger()
    ledger.append(
        event_type="claim.staled",
        tenant_id="t",
        workspace_id="w",
        goal_id="g1",
        payload={"claim_id": "c1", "new_status": "STALE"},
        producer="test",
    )
    ledger.append(
        event_type="claim.contradicted",
        tenant_id="t",
        workspace_id="w",
        goal_id="g1",
        payload={"claim_id": "c1"},
        producer="test",
    )
    engine = EventReplayEngine(ledger)
    at0 = engine.rebuild_status_projection(
        goal_id="g1", until_index=0, record_rebuild_event=False
    )
    assert at0["claim"] == {}
    at1 = engine.rebuild_status_projection(
        goal_id="g1",
        until_index=1,
        record_rebuild_event=False,
        seed={"claim": {"c1": "ACTIVE"}},
    )
    assert at1["claim"]["c1"] == "STALE"
    cmp = engine.compare_at(
        index_a=1,
        index_b=2,
        goal_id="g1",
        seed={"claim": {"c1": "ACTIVE"}},
    )
    assert cmp["at_a"]["claim"]["c1"] == "STALE"
    assert cmp["at_b"]["claim"]["c1"] == "CONTRADICTED"


def test_cli_events_replay_help() -> None:
    # Smoke: parser accepts replay subcommand
    try:
        main(["events", "replay", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
