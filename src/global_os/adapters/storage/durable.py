"""Durable store connection port — Postgres is one impl; never silent SQLite fallback."""

from __future__ import annotations

import os
import sqlite3
from typing import Any

from global_os.adapters.storage.sql import connect_sqlite


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
            import psycopg  # type: ignore[import-not-found]
        except ImportError as exc:
            raise PostgresUnavailable(
                "DATABASE_URL requests Postgres but psycopg is not installed; "
                "refusing silent SQLite fallback"
            ) from exc
        conn = psycopg.connect(url)
        return conn

    raise DurableStoreError(f"unsupported DATABASE_URL scheme: {url!r}")


def assert_sqlite_connection(conn: Any) -> sqlite3.Connection:
    if not isinstance(conn, sqlite3.Connection):
        raise DurableStoreError("expected sqlite3.Connection")
    return conn
