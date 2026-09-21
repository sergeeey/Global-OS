from __future__ import annotations

from global_os.adapters.storage import SqlEventLedger, SqlGoalStore, connect_sqlite


def test_sql_ledger_and_goal_persist(sample_goal):
    conn = connect_sqlite(":memory:")
    ledger = SqlEventLedger(conn)
    goals = SqlGoalStore(conn, ledger)
    g1 = goals.create(sample_goal(goal_id="goal_sql_001"))
    assert g1["version"] == 1
    g2 = goals.amend(
        "goal_sql_001",
        changes={"non_goals": ["x", "y"]},
        proposer="user",
        reason="extend",
        changed_fields=["non_goals"],
    )
    assert g2["version"] == 2
    assert goals.get("goal_sql_001", version=1)["content_hash"] == g1["content_hash"]
    assert len(ledger) >= 2
    types = [e["event_type"] for e in ledger.list_events(goal_id="goal_sql_001")]
    assert "goal.created" in types
    assert "goal.amended" in types
