"""Durable replay / idempotency store for ExecutionToken jti + Gateway receipts.

In-process dicts do not survive crash/restart. This store is the minimum
durable gate for GOS-I03 replay protection (sqlite file or :memory:).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol


class DurableGateStore(Protocol):
    def jti_consumed(self, jti: str) -> bool: ...

    def consume_jti(self, jti: str) -> bool:
        """Atomically mark jti consumed. Returns False if already consumed."""
        ...

    def get_idempotent_receipt(self, idempotency_key: str) -> dict[str, Any] | None: ...

    def claim_idempotency(self, idempotency_key: str) -> bool:
        """Reserve key before side effect. False if already claimed/completed."""
        ...

    def put_idempotent_receipt(self, idempotency_key: str, receipt: dict[str, Any]) -> None: ...


@dataclass
class MemoryDurableGateStore:
    """Process-local fallback (explicitly non-durable). Prefer SqliteDurableGateStore."""

    durable: bool = False

    def __post_init__(self) -> None:
        self._jti: set[str] = set()
        self._idem: dict[str, dict[str, Any]] = {}
        self._claimed: set[str] = set()

    def jti_consumed(self, jti: str) -> bool:
        return jti in self._jti

    def consume_jti(self, jti: str) -> bool:
        if jti in self._jti:
            return False
        self._jti.add(jti)
        return True

    def get_idempotent_receipt(self, idempotency_key: str) -> dict[str, Any] | None:
        return self._idem.get(idempotency_key)

    def claim_idempotency(self, idempotency_key: str) -> bool:
        if idempotency_key in self._claimed or idempotency_key in self._idem:
            return False
        self._claimed.add(idempotency_key)
        return True

    def put_idempotent_receipt(self, idempotency_key: str, receipt: dict[str, Any]) -> None:
        self._claimed.add(idempotency_key)
        self._idem[idempotency_key] = receipt


class SqliteDurableGateStore:
    """SQLite-backed consumed jti + idempotency receipts (survives process restart)."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        # check_same_thread=False for simple test reuse; production uses one writer
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        # NORMAL: fsync at critical moments; with WAL still crash-safe for process
        # kill. FULL (sqlite default) is ~30–40× slower on this path and is not
        # required for GOS durable gate semantics (jti/idempotency durability).
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA temp_store=MEMORY")
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS consumed_jti (
              jti TEXT PRIMARY KEY,
              consumed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS idempotency_receipts (
              idempotency_key TEXT PRIMARY KEY,
              receipt_json TEXT,
              status TEXT NOT NULL,
              stored_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    @property
    def durable(self) -> bool:
        return self.path != ":memory:"

    def close(self) -> None:
        self._conn.close()

    def jti_consumed(self, jti: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM consumed_jti WHERE jti = ?", (jti,)
        ).fetchone()
        return row is not None

    def consume_jti(self, jti: str) -> bool:
        try:
            self._conn.execute(
                "INSERT INTO consumed_jti (jti, consumed_at) VALUES (?, ?)",
                (jti, datetime.now(UTC).isoformat()),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_idempotent_receipt(self, idempotency_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT receipt_json, status FROM idempotency_receipts WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        if row is None:
            return None
        if row["status"] != "COMPLETE" or row["receipt_json"] is None:
            return None
        raw = json.loads(str(row["receipt_json"]))
        if not isinstance(raw, dict):
            raise TypeError("idempotency receipt must be object")
        return raw

    def claim_idempotency(self, idempotency_key: str) -> bool:
        try:
            self._conn.execute(
                """
                INSERT INTO idempotency_receipts
                  (idempotency_key, receipt_json, status, stored_at)
                VALUES (?, NULL, 'CLAIMED', ?)
                """,
                (idempotency_key, datetime.now(UTC).isoformat()),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def put_idempotent_receipt(self, idempotency_key: str, receipt: dict[str, Any]) -> None:
        payload = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        self._conn.execute(
            """
            INSERT INTO idempotency_receipts
              (idempotency_key, receipt_json, status, stored_at)
            VALUES (?, ?, 'COMPLETE', ?)
            ON CONFLICT(idempotency_key) DO UPDATE SET
              receipt_json = excluded.receipt_json,
              status = 'COMPLETE',
              stored_at = excluded.stored_at
            """,
            (idempotency_key, payload, datetime.now(UTC).isoformat()),
        )
        self._conn.commit()
