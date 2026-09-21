"""Negative / null-result memory (GOS-I11)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.common.hashing import new_id
from global_os.runtime.events.ledger import EventLedger


class NullResultStore:
    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._items: dict[str, dict[str, Any]] = {}

    def record(
        self,
        *,
        attempt: str,
        why_failed: str,
        evidence: list[str],
        conditions: str,
        reopen_condition: str,
        tenant_id: str,
        workspace_id: str,
        goal_id: str | None = None,
    ) -> dict[str, Any]:
        item_id: str = new_id("nr")
        item: dict[str, Any] = {
            "id": item_id,
            "attempt": attempt,
            "why_failed": why_failed,
            "evidence": list(evidence),
            "conditions": conditions,
            "reopen_condition": reopen_condition,
        }
        self._items[item_id] = item
        self._ledger.append(
            event_type="null_result.recorded",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload=item,
            producer="memory.negative",
        )
        return deepcopy(item)

    def warn_if_repeat(self, attempt: str) -> str | None:
        for item in self._items.values():
            if item["attempt"] == attempt:
                return (
                    f"repeated rejected approach without reopen: {attempt}; "
                    f"reopen_condition={item['reopen_condition']}"
                )
        return None

    def list_all(self) -> list[dict[str, Any]]:
        return deepcopy(list(self._items.values()))
