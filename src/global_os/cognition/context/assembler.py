"""Context assembler — typed retrieval into model calls; not full memory dump."""

from __future__ import annotations

from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate


class ContextAssembler:
    def assemble(
        self,
        *,
        goal_id: str,
        token_budget: int,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Select context items by priority until token_budget exhausted.

        Each candidate must already carry provenance fields (or be completed here).
        """
        selected: list[dict[str, Any]] = []
        used = 0
        for raw in sorted(candidates, key=lambda c: c.get("priority", 100)):
            item = {
                "id": raw.get("id") or new_id("ctx"),
                "schema_version": "0.1.0",
                "source": raw["source"],
                "type": raw["type"],
                "trust": raw["trust"],
                "freshness": raw.get("freshness", "unknown"),
                "goal_scope": raw.get("goal_scope", goal_id),
                "token_cost": int(raw.get("token_cost", 0)),
                "reason_included": raw["reason_included"],
                "content_ref": raw.get("content_ref"),
            }
            item = {k: v for k, v in item.items() if v is not None}
            validate(item, "context_item.schema.json")
            if used + item["token_cost"] > token_budget:
                continue
            selected.append(item)
            used += item["token_cost"]
        return selected
