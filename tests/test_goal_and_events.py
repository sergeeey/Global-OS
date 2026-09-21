from __future__ import annotations

import pytest

from global_os.runtime.events import AppendOnlyViolation, EventLedger
from global_os.runtime.goals import GoalMutationError, GoalStore


def test_goal_create_and_immutable_amend(sample_goal):
    ledger = EventLedger()
    store = GoalStore(ledger)
    g1 = store.create(sample_goal())
    assert g1["version"] == 1
    hash_v1 = g1["content_hash"]

    g2 = store.amend(
        g1["goal_id"],
        changes={"non_goals": ["modify_production", "contact_suppliers"]},
        proposer="user_serge",
        reason="clarify non-goals",
        changed_fields=["non_goals"],
    )
    assert g2["version"] == 2
    assert g2["supersedes_version"] == 1

    still_v1 = store.get(g1["goal_id"], version=1)
    assert still_v1["content_hash"] == hash_v1
    assert still_v1["non_goals"] == ["modify_production"]

    types = [e["event_type"] for e in ledger.list_events(goal_id=g1["goal_id"])]
    assert types == ["goal.created", "goal.amended"]


def test_goal_overwrite_forbidden(sample_goal):
    ledger = EventLedger()
    store = GoalStore(ledger)
    g = store.create(sample_goal(goal_id="goal_x"))
    with pytest.raises(GoalMutationError):
        store.overwrite_forbidden(g["goal_id"], sample_goal(goal_id="goal_x", version=99))


def test_event_ledger_append_only():
    ledger = EventLedger()
    ledger.append(
        event_type="null_result.recorded",
        tenant_id="t",
        workspace_id="w",
        payload={"attempt": "x", "why_failed": "y"},
        producer="test",
    )
    with pytest.raises(AppendOnlyViolation):
        ledger.mutate_forbidden(0, payload={})
