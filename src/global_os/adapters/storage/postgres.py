"""Postgres durable store — real shared-state backend (ADR-0005)."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.adapters.storage.durable import apply_postgres_migrations, connect_durable_store
from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import AppendOnlyViolation, EventLedger


class PostgresEventLedger(EventLedger):
    """Append-only ledger on Postgres. Domain API matches EventLedger."""

    def __init__(self, conn: Any) -> None:
        super().__init__()
        self._conn = conn
        self._seq = self._max_seq()

    def _max_seq(self) -> int:
        row = self._conn.execute("SELECT COALESCE(MAX(seq), 0) AS m FROM events").fetchone()
        return int(row["m"])

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
        digest_source = {k: v for k, v in body.items() if v is not None}
        event: dict[str, Any] = {
            "event_id": new_id("evt"),
            "schema_version": "0.1.0",
            "recorded_at": now,
            "content_hash": content_hash(digest_source),
            **body,
        }
        event = {k: v for k, v in event.items() if v is not None}
        validate(event, "event.schema.json")
        row = self._conn.execute("SELECT nextval('gos_events_seq') AS n").fetchone()
        self._seq = int(row["n"])
        self._conn.execute(
            """
            INSERT INTO events (
                event_id, event_type, schema_version, tenant_id, workspace_id,
                goal_id, task_id, org_unit_id, principal_id, occurred_at, recorded_at,
                payload, causation_id, correlation_id, producer, content_hash, seq
            ) VALUES (
                %(event_id)s, %(event_type)s, %(schema_version)s, %(tenant_id)s, %(workspace_id)s,
                %(goal_id)s, %(task_id)s, %(org_unit_id)s, %(principal_id)s, %(occurred_at)s,
                %(recorded_at)s, %(payload)s, %(causation_id)s, %(correlation_id)s,
                %(producer)s, %(content_hash)s, %(seq)s
            )
            """,
            {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "schema_version": event["schema_version"],
                "tenant_id": event["tenant_id"],
                "workspace_id": event["workspace_id"],
                "goal_id": event.get("goal_id"),
                "task_id": event.get("task_id"),
                "org_unit_id": event.get("org_unit_id"),
                "principal_id": event.get("principal_id"),
                "occurred_at": event["occurred_at"],
                "recorded_at": event["recorded_at"],
                "payload": json.dumps(event["payload"], ensure_ascii=False),
                "causation_id": event.get("causation_id"),
                "correlation_id": event.get("correlation_id"),
                "producer": event["producer"],
                "content_hash": event["content_hash"],
                "seq": self._seq,
            },
        )
        self._conn.commit()
        return deepcopy(event)

    def __len__(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()
        return int(row["c"])

    def list_events(self, goal_id: str | None = None) -> list[dict[str, Any]]:
        if goal_id is None:
            rows = self._conn.execute("SELECT * FROM events ORDER BY seq").fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE goal_id = %(goal_id)s ORDER BY seq",
                {"goal_id": goal_id},
            ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item["payload"])
            item.pop("seq", None)
            out.append({k: v for k, v in item.items() if v is not None})
        return out

    def mutate_forbidden(self, index: int, **_kwargs: Any) -> None:
        raise AppendOnlyViolation("Event ledger is append-only; mutation forbidden")


def open_postgres_ledger(database_url: str) -> tuple[Any, PostgresEventLedger]:
    """Connect, migrate, return (conn, ledger)."""
    conn = connect_durable_store(database_url)
    from psycopg.rows import dict_row

    conn.row_factory = dict_row
    apply_postgres_migrations(conn)
    # Create sequence once; never reset on every open (would race concurrent writers).
    conn.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'gos_events_seq'
          ) THEN
            CREATE SEQUENCE gos_events_seq;
            PERFORM setval(
              'gos_events_seq',
              GREATEST((SELECT COALESCE(MAX(seq), 0) FROM events), 1),
              (SELECT COALESCE(MAX(seq), 0) FROM events) > 0
            );
          ELSIF (SELECT COALESCE(MAX(seq), 0) FROM events)
                > (SELECT last_value FROM gos_events_seq) THEN
            PERFORM setval(
              'gos_events_seq',
              (SELECT MAX(seq) FROM events),
              true
            );
          END IF;
        END$$;
        """
    )
    conn.commit()
    return conn, PostgresEventLedger(conn)
