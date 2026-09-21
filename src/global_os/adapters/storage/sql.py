"""SQL store backends — SQLite for local/tests, Postgres when DATABASE_URL set."""

from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import AppendOnlyViolation, EventLedger


def _migrations_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        candidate = parent / "migrations"
        if candidate.is_dir() and any(candidate.glob("*.sql")):
            return candidate
    raise FileNotFoundError("migrations/ not found")


def apply_migrations(conn: sqlite3.Connection, migrations_dir: Path | None = None) -> None:
    root = migrations_dir or _migrations_dir()
    for path in sorted(root.glob("*.sql")):
        conn.executescript(path.read_text(encoding="utf-8"))
    conn.commit()


def connect_sqlite(path: str | Path = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    apply_migrations(conn)
    return conn


class SqlEventLedger(EventLedger):
    """Append-only ledger backed by SQL (SQLite now, Postgres-compatible schema)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
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
        self._seq += 1
        self._conn.execute(
            """
            INSERT INTO events (
                event_id, event_type, schema_version, tenant_id, workspace_id,
                goal_id, task_id, org_unit_id, principal_id, occurred_at, recorded_at,
                payload, causation_id, correlation_id, producer, content_hash, seq
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["event_type"],
                event["schema_version"],
                event["tenant_id"],
                event["workspace_id"],
                event.get("goal_id"),
                event.get("task_id"),
                event.get("org_unit_id"),
                event.get("principal_id"),
                event["occurred_at"],
                event["recorded_at"],
                json.dumps(event["payload"], ensure_ascii=False),
                event.get("causation_id"),
                event.get("correlation_id"),
                event["producer"],
                event["content_hash"],
                self._seq,
            ),
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
                "SELECT * FROM events WHERE goal_id = ? ORDER BY seq", (goal_id,)
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


class SqlGoalStore:
    """Immutable versioned goals in SQL."""

    def __init__(self, conn: sqlite3.Connection, ledger: EventLedger) -> None:
        self._conn = conn
        self._ledger = ledger

    def create(self, draft: dict[str, Any]) -> dict[str, Any]:
        from global_os.runtime.goals.store import GoalStore

        # Reuse validation/hash via in-memory helper then persist
        mem = GoalStore(self._ledger)
        goal = mem.create(draft)
        self._insert(goal)
        return goal

    def _insert(self, goal: dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT INTO goals (goal_id, version, tenant_id, workspace_id, body, content_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                goal["goal_id"],
                goal["version"],
                goal["tenant_id"],
                goal["workspace_id"],
                json.dumps(goal, ensure_ascii=False),
                goal["content_hash"],
                goal["created_at"],
            ),
        )
        self._conn.commit()

    def get(self, goal_id: str, version: int | None = None) -> dict[str, Any]:
        if version is None:
            row = self._conn.execute(
                "SELECT body FROM goals WHERE goal_id = ? ORDER BY version DESC LIMIT 1",
                (goal_id,),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT body FROM goals WHERE goal_id = ? AND version = ?",
                (goal_id, version),
            ).fetchone()
        if row is None:
            from global_os.runtime.goals.store import GoalNotFoundError

            raise GoalNotFoundError(f"{goal_id}@v{version}")
        body = json.loads(row["body"])
        if not isinstance(body, dict):
            raise TypeError("goal body must be object")
        return cast(dict[str, Any], body)

    def amend(
        self,
        goal_id: str,
        *,
        changes: dict[str, Any],
        proposer: str,
        reason: str,
        changed_fields: list[str],
        authority_ref: str | None = None,
        approval_ref: str | None = None,
        impact_analysis: str | None = None,
    ) -> dict[str, Any]:
        from global_os.runtime.goals.store import GoalStore

        # Load all versions into memory GoalStore to keep amend semantics
        rows = self._conn.execute(
            "SELECT body FROM goals WHERE goal_id = ? ORDER BY version", (goal_id,)
        ).fetchall()
        if not rows:
            from global_os.runtime.goals.store import GoalNotFoundError

            raise GoalNotFoundError(goal_id)
        mem = GoalStore(self._ledger)
        mem._versions[goal_id] = [json.loads(r["body"]) for r in rows]
        # Avoid duplicate goal.created on ledger — only amend events from here
        new_goal = mem.amend(
            goal_id,
            changes=changes,
            proposer=proposer,
            reason=reason,
            changed_fields=changed_fields,
            authority_ref=authority_ref,
            approval_ref=approval_ref,
            impact_analysis=impact_analysis,
        )
        self._insert(new_goal)
        return new_goal
