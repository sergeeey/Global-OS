"""Isolation + durability profile guards for perf-safe copies / sqlite sync."""

from __future__ import annotations

from pathlib import Path

import pytest
from jsonschema import ValidationError

from global_os.adapters.storage.sql import connect_sqlite
from global_os.common.jsonable import jsonable_copy
from global_os.contracts.validate import validate
from global_os.kernel.authority.durable_gate import SqliteDurableGateStore
from global_os.runtime.events.ledger import EventLedger


def test_jsonable_copy_isolates_nested_mutation() -> None:
    src = {"payload": {"n": 1, "L": [1, 2]}, "x": "y"}
    dst = jsonable_copy(src)
    dst["payload"]["n"] = 99
    dst["payload"]["L"].append(3)
    assert src["payload"]["n"] == 1
    assert src["payload"]["L"] == [1, 2]


def test_ledger_append_return_isolated() -> None:
    ledger = EventLedger()
    ev = ledger.append(
        event_type="null_result.recorded",
        tenant_id="t",
        workspace_id="w",
        payload={"k": [1]},
        producer="test",
    )
    ev["payload"]["k"].append(2)
    listed = ledger.list_events()
    assert listed[0]["payload"]["k"] == [1]


def test_validator_cache_still_rejects_bad_event() -> None:
    with pytest.raises(ValidationError):
        validate({"event_id": "bad"}, "event.schema.json")


def test_durable_gate_keeps_full_synchronous(tmp_path: Path) -> None:
    """Authority jti/idempotency must not silently weaken to NORMAL."""
    store = SqliteDurableGateStore(tmp_path / "gate.sqlite")
    try:
        mode = store._conn.execute("PRAGMA synchronous").fetchone()[0]
        # SQLite: 0=OFF, 1=NORMAL, 2=FULL, 3=EXTRA
        assert int(mode) == 2
    finally:
        store.close()


def test_connect_sqlite_defaults_to_full_synchronous(tmp_path: Path) -> None:
    conn = connect_sqlite(tmp_path / "events.sqlite")
    try:
        mode = conn.execute("PRAGMA synchronous").fetchone()[0]
        assert int(mode) == 2
    finally:
        conn.close()


def test_connect_sqlite_allows_normal_for_rebuildable_cache(tmp_path: Path) -> None:
    conn = connect_sqlite(tmp_path / "cache.sqlite", synchronous="NORMAL")
    try:
        mode = conn.execute("PRAGMA synchronous").fetchone()[0]
        assert int(mode) == 1
    finally:
        conn.close()
