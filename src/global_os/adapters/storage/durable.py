"""Durable store connection port — Postgres is one impl; never silent SQLite fallback."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from global_os.adapters.storage.sql import _migrations_dir, connect_sqlite


class DurableStoreError(Exception):
    pass


class PostgresUnavailable(DurableStoreError):
    """Fail-closed when Postgres was requested but cannot be used."""


def connect_durable_store(database_url: str | None = None) -> Any:
    """Return a DB connection.

    - sqlite:// or unset/empty → SQLite (local/dev)
    - postgres:// or postgresql:// → requires psycopg; never falls back to SQLite
    """
    url = database_url if database_url is not None else os.environ.get("DATABASE_URL", "")
    url = (url or "").strip()
    if not url or url.startswith("sqlite:"):
        path = ":memory:"
        if url.startswith("sqlite:///"):
            path = url.removeprefix("sqlite:///")
        elif url.startswith("sqlite://"):
            path = url.removeprefix("sqlite://") or ":memory:"
        return connect_sqlite(path)

    if url.startswith(("postgres://", "postgresql://")):
        try:
            import psycopg
        except ImportError as exc:
            raise PostgresUnavailable(
                "DATABASE_URL requests Postgres but psycopg is not installed; "
                "refusing silent SQLite fallback"
            ) from exc
        try:
            conn = psycopg.connect(url, connect_timeout=2)
        except Exception as exc:
            raise PostgresUnavailable(
                f"Postgres unreachable/unavailable ({exc}); refusing silent SQLite fallback"
            ) from exc
        return conn

    raise DurableStoreError(f"unsupported DATABASE_URL scheme: {url!r}")


def apply_postgres_migrations(conn: Any, migrations_dir: Path | None = None) -> int:
    """Apply SQL migrations on a live Postgres connection. Returns statements executed."""
    root = migrations_dir or _migrations_dir()
    count = 0
    for path in sorted(root.glob("*.sql")):
        raw_lines = path.read_text(encoding="utf-8").splitlines()
        cleaned: list[str] = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            cleaned.append(line)
        sql = "\n".join(cleaned)
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            conn.execute(stmt)
            count += 1
        conn.commit()
    return count


def assert_sqlite_connection(conn: Any) -> sqlite3.Connection:
    if not isinstance(conn, sqlite3.Connection):
        raise DurableStoreError("expected sqlite3.Connection")
    return conn
