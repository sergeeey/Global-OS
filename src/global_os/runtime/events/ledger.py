"""Append-only event ledger (in-memory; Postgres later)."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate


class EventLedgerError(Exception):
    pass


class AppendOnlyViolation(EventLedgerError):
    pass


class EventLedger:
    """In-memory append-only ledger with schema validation."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def append(
        self,
        *,
        event_type: str,
        tenant_id: str,
        workspace_id: str,
        payload: dict[str, Any],
        producer: str,
        goal_id: str | None = None,
        task_id: str | None = None,
        org_unit_id: str | None = None,
        principal_id: str | None = None,
        causation_id: str | None = None,
        correlation_id: str | None = None,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        body = {
            "event_type": event_type,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "payload": payload,
            "producer": producer,
            "goal_id": goal_id,
            "task_id": task_id,
            "org_unit_id": org_unit_id,
            "principal_id": principal_id,
            "causation_id": causation_id,
            "correlation_id": correlation_id,
            "occurred_at": occurred_at or now,
        }
        # Hash excludes recorded_at/event_id to keep content stable for digest of domain fields
        digest_source = {k: v for k, v in body.items() if v is not None}
        event: dict[str, Any] = {
            "event_id": new_id("evt"),
            "schema_version": "0.1.0",
            "recorded_at": now,
            "content_hash": content_hash(digest_source),
            **body,
        }
        # Drop None optional fields before schema validate
        event = {k: v for k, v in event.items() if v is not None}
        validate(event, "event.schema.json")
        self._events.append(event)
        return deepcopy(event)

    def __len__(self) -> int:
        return len(self._events)

    def list_events(self, goal_id: str | None = None) -> list[dict[str, Any]]:
        events = self._events
        if goal_id is not None:
            events = [e for e in events if e.get("goal_id") == goal_id]
        return deepcopy(events)

    def mutate_forbidden(self, index: int, **_kwargs: Any) -> None:
        """Guard for tests — ledger entries are immutable."""
        raise AppendOnlyViolation("Event ledger is append-only; mutation forbidden")
