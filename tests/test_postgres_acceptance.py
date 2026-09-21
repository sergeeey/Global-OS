"""Postgres durable shared-state acceptance — skip if DATABASE_URL unset / unreachable."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

import pytest

from global_os.adapters.storage import PostgresUnavailable, connect_durable_store
from global_os.adapters.storage.postgres import open_postgres_ledger


def _pg_url() -> str | None:
    return os.environ.get("DATABASE_URL") or os.environ.get("GOS_TEST_DATABASE_URL")


@pytest.fixture
def pg_url() -> str:
    url = _pg_url()
    if not url or not url.startswith(("postgres://", "postgresql://")):
        pytest.skip("DATABASE_URL / GOS_TEST_DATABASE_URL not set for Postgres acceptance")
    try:
        connect_durable_store(url).close()
    except PostgresUnavailable:
        pytest.skip("Postgres unreachable")
    return url


def test_postgres_events_survive_reconnect(pg_url: str):
    conn1, ledger1 = open_postgres_ledger(pg_url)
    # isolate table for this test run
    conn1.execute("DELETE FROM events")
    conn1.commit()
    evt = ledger1.append(
        event_type="goal.created",
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_pg_1",
        payload={"k": "v"},
        producer="test.postgres",
    )
    conn1.close()

    conn2, ledger2 = open_postgres_ledger(pg_url)
    events = ledger2.list_events(goal_id="goal_pg_1")
    assert any(e["event_id"] == evt["event_id"] for e in events)
    assert len(ledger2) >= 1
    conn2.close()


def test_postgres_concurrent_writers(pg_url: str):
    # ensure schema
    conn0, _ = open_postgres_ledger(pg_url)
    conn0.execute("DELETE FROM events WHERE producer = 'test.postgres.concurrent'")
    conn0.commit()
    conn0.close()

    def write_one(i: int) -> str:
        conn, ledger = open_postgres_ledger(pg_url)
        evt = ledger.append(
            event_type="null_result.recorded",
            tenant_id="t",
            workspace_id="w",
            goal_id=f"goal_pg_c_{i}",
            payload={"i": i},
            producer="test.postgres.concurrent",
        )
        conn.close()
        return evt["event_id"]

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(write_one, range(8)))
    assert len(ids) == len(set(ids))

    conn, ledger = open_postgres_ledger(pg_url)
    found = [
        e
        for e in ledger.list_events()
        if e.get("producer") == "test.postgres.concurrent"
    ]
    assert len(found) >= 8
    conn.close()
