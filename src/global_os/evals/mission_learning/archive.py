"""Append-only mission / candidate archive for MLLv0 (process-local)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from global_os.evals.mission_learning.schemas import (
    validate_improvement_candidate,
    validate_mission_record,
)


@dataclass
class MissionArchive:
    """In-memory + optional directory persistence; never auto-promotes."""

    records: list[dict[str, Any]] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    tournament_results: list[dict[str, Any]] = field(default_factory=list)

    def add_mission(self, record: dict[str, Any]) -> dict[str, Any]:
        validated = validate_mission_record(record)
        self.records.append(dict(validated))
        return validated

    def add_candidate(self, cand: dict[str, Any]) -> dict[str, Any]:
        validated = validate_improvement_candidate(cand)
        self.candidates.append(dict(validated))
        return validated

    def add_tournament_result(self, result: dict[str, Any]) -> None:
        if result.get("auto_promoted") is True:
            raise ValueError("archive refuses auto_promoted=true")
        self.tournament_results.append(dict(result))

    def persist(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "missions.json").write_text(
            json.dumps(self.records, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (directory / "candidates.json").write_text(
            json.dumps(self.candidates, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (directory / "tournament.json").write_text(
            json.dumps(self.tournament_results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
