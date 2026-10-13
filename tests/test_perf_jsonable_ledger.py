"""Isolation + interface stability for jsonable_copy ledger returns."""

from __future__ import annotations

from global_os.common.jsonable import jsonable_copy
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
    import pytest
    from jsonschema import ValidationError

    from global_os.contracts.validate import validate

    with pytest.raises(ValidationError):
        validate({"event_id": "bad"}, "event.schema.json")
