"""Evaluator registry — calibrated judges; judge cannot self-validate (GOS-I24)."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.contracts.validate import validate


class EvaluatorError(Exception):
    pass


class EvaluatorRegistry:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def register(self, descriptor: dict[str, Any]) -> None:
        validate(descriptor, "evaluator_descriptor.schema.json")
        # GOS-I24: refuse self-only calibration markers
        cal = descriptor.get("calibrated_on", {})
        if cal.get("dataset_id") in {"self", "self_judge", "model_self"}:
            raise EvaluatorError("judge cannot validate itself (GOS-I24)")
        self._items[descriptor["id"]] = deepcopy(descriptor)

    def get(self, evaluator_id: str) -> dict[str, Any]:
        return deepcopy(self._items[evaluator_id])

    def is_valid(self, evaluator_id: str, *, now: datetime | None = None) -> bool:
        item = self._items[evaluator_id]
        current = now or datetime.now(UTC)
        return datetime.fromisoformat(item["valid_until"]) >= current
