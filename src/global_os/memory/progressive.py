"""Progressive disclosure memory + commit boundary (Letta-inspired, ADR-0013).

Root index stays in context; path bodies load on demand. Durable promotion only
via explicit draft → proposed → committed (ledger event). Tool success never
silently becomes committed memory.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from global_os.common.hashing import new_id
from global_os.runtime.events.ledger import EventLedger


class MemoryStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"


@dataclass
class MemoryEntry:
    path: str
    body: str
    status: MemoryStatus
    entry_id: str
    epistemic_kind: str  # observation|belief|claim|procedure|negative — not mixed
    token_cost: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "path": self.path,
            "body": self.body,
            "status": self.status.value,
            "epistemic_kind": self.epistemic_kind,
            "token_cost": self.token_cost,
            "meta": dict(self.meta),
        }


ROOT_INDEX_PATH = "MEMORY.md"


class ProgressiveMemoryStore:
    """Path-addressable memory with commit-boundary promotion."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._entries: dict[str, MemoryEntry] = {}
        # Ensure root index exists as committed skeleton.
        root_id = new_id("mem")
        self._entries[ROOT_INDEX_PATH] = MemoryEntry(
            path=ROOT_INDEX_PATH,
            body="# Memory index\n",
            status=MemoryStatus.COMMITTED,
            entry_id=root_id,
            epistemic_kind="procedure",
            token_cost=16,
        )

    def draft(
        self,
        *,
        path: str,
        body: str,
        epistemic_kind: str,
        tenant_id: str,
        workspace_id: str,
        goal_id: str | None = None,
        token_cost: int | None = None,
    ) -> dict[str, Any]:
        if path == ROOT_INDEX_PATH:
            raise ValueError("root index is not drafted via draft(); use update_index")
        if epistemic_kind not in {
            "observation",
            "belief",
            "claim",
            "procedure",
            "negative",
            "preference",
        }:
            raise ValueError(f"invalid epistemic_kind: {epistemic_kind}")
        entry = MemoryEntry(
            path=path,
            body=body,
            status=MemoryStatus.DRAFT,
            entry_id=new_id("mem"),
            epistemic_kind=epistemic_kind,
            token_cost=token_cost if token_cost is not None else max(1, len(body) // 4),
        )
        self._entries[path] = entry
        self._ledger.append(
            event_type="memory.drafted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload=entry.to_dict(),
            producer="memory.progressive",
        )
        return entry.to_dict()

    def propose(
        self,
        path: str,
        *,
        tenant_id: str,
        workspace_id: str,
        goal_id: str | None = None,
    ) -> dict[str, Any]:
        entry = self._require(path)
        if entry.status is not MemoryStatus.DRAFT:
            raise ValueError(f"propose requires DRAFT, got {entry.status.value}")
        entry.status = MemoryStatus.PROPOSED
        self._ledger.append(
            event_type="memory.proposed",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload={"path": path, "entry_id": entry.entry_id},
            producer="memory.progressive",
        )
        return entry.to_dict()

    def commit(
        self,
        path: str,
        *,
        tenant_id: str,
        workspace_id: str,
        goal_id: str | None = None,
    ) -> dict[str, Any]:
        entry = self._require(path)
        if entry.status is not MemoryStatus.PROPOSED:
            raise ValueError(f"commit requires PROPOSED, got {entry.status.value}")
        entry.status = MemoryStatus.COMMITTED
        # Update root index listing.
        root = self._entries[ROOT_INDEX_PATH]
        line = f"- [{path}]({path}) ({entry.epistemic_kind})\n"
        if path not in root.body:
            root.body += line
            root.token_cost = max(1, len(root.body) // 4)
        self._ledger.append(
            event_type="memory.committed",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            payload=entry.to_dict(),
            producer="memory.progressive",
        )
        return entry.to_dict()

    def reject_silent_promote_from_tool(self, tool_payload: dict[str, Any]) -> None:
        """Tool success must not become committed memory (GOS / ADR-0013)."""
        raise PermissionError(
            "silent memory promotion from tool success is forbidden; "
            f"use draft→propose→commit (tool keys={sorted(tool_payload.keys())})"
        )

    def context_candidates(
        self,
        *,
        include_paths: list[str] | None = None,
        root_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Build ContextAssembler candidates. Default: root index only."""
        paths = [ROOT_INDEX_PATH] if root_only else list(self._entries)
        if include_paths:
            for p in include_paths:
                if p not in paths:
                    paths.append(p)
        out: list[dict[str, Any]] = []
        for path in paths:
            entry = self._entries.get(path)
            if entry is None or entry.status is not MemoryStatus.COMMITTED:
                continue
            priority = 0 if path == ROOT_INDEX_PATH else 50
            # Map memory epistemic kinds → ContextItem schema enums.
            type_map = {
                "observation": "observation",
                "belief": "belief",
                "claim": "note",
                "procedure": "procedure",
                "negative": "note",
                "preference": "constraint",
            }
            out.append(
                {
                    # ContextAssembler schema requires ctx_* ids (not mem_*).
                    "id": new_id("ctx"),
                    "source": f"memory:{path}",
                    "type": type_map.get(entry.epistemic_kind, "note"),
                    "trust": "ORG_TRUSTED",
                    "freshness": "committed",
                    "token_cost": entry.token_cost if path == ROOT_INDEX_PATH else 0,
                    "reason_included": (
                        "root_index" if path == ROOT_INDEX_PATH else f"requested:{path}"
                    ),
                    "content_ref": path,
                    "priority": priority,
                }
            )
        return out

    def retrieve(self, path: str) -> dict[str, Any]:
        entry = self._require(path)
        if entry.status is not MemoryStatus.COMMITTED:
            raise PermissionError(f"retrieve only COMMITTED paths; {path} is {entry.status.value}")
        return entry.to_dict()

    def list_committed(self) -> list[dict[str, Any]]:
        return [
            deepcopy(e.to_dict())
            for e in self._entries.values()
            if e.status is MemoryStatus.COMMITTED
        ]

    def _require(self, path: str) -> MemoryEntry:
        if path not in self._entries:
            raise KeyError(f"unknown memory path: {path}")
        return self._entries[path]
