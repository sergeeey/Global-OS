"""Simple JSON file persistence for local CLI (not production store)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore


class FileRuntime:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd() / ".gos"
        self.root.mkdir(parents=True, exist_ok=True)
        self._goals_path = self.root / "goals.json"
        self._events_path = self.root / "events.json"
        self.ledger = EventLedger()
        self.goals = GoalStore(self.ledger)
        self._load()

    def _load(self) -> None:
        if self._events_path.exists():
            events = json.loads(self._events_path.read_text(encoding="utf-8"))
            self.ledger._events = events
        if self._goals_path.exists():
            data = json.loads(self._goals_path.read_text(encoding="utf-8"))
            self.goals._versions = data

    def save(self) -> None:
        self._goals_path.write_text(
            json.dumps(self.goals._versions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._events_path.write_text(
            json.dumps(self.ledger.list_events(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
