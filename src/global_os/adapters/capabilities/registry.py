"""Capability Registry — volatile layer between Stable Core and World Facts (GOS-I25)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.contracts.validate import validate


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def register(self, descriptor: dict[str, Any]) -> None:
        validate(descriptor, "capability_descriptor.schema.json")
        self._items[descriptor["id"]] = deepcopy(descriptor)

    def get(self, cap_id: str) -> dict[str, Any]:
        return deepcopy(self._items[cap_id])

    def find(
        self,
        *,
        kind: str | None = None,
        required_tags: set[str] | None = None,
        max_risk: str | None = None,
    ) -> list[dict[str, Any]]:
        risk_order = ["none", "low", "moderate", "high", "critical"]
        out: list[dict[str, Any]] = []
        for item in self._items.values():
            if kind and item["kind"] != kind:
                continue
            tags = set(item.get("capabilities", []))
            if required_tags and not required_tags.issubset(tags):
                continue
            if max_risk is not None and risk_order.index(item["risk"]) > risk_order.index(
                max_risk
            ):
                continue
            out.append(deepcopy(item))
        return out
