"""Immutable versioned Goal Contract store (GOS-I06)."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class GoalMutationError(Exception):
    pass


class GoalNotFoundError(Exception):
    pass


class GoalStore:
    """Goals are never overwritten; amendments create a new version."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        # goal_id -> list of versions (1-indexed by position+1)
        self._versions: dict[str, list[dict[str, Any]]] = {}

    def create(self, draft: dict[str, Any]) -> dict[str, Any]:
        goal = deepcopy(draft)
        goal.setdefault("schema_version", "0.1.0")
        goal.setdefault("version", 1)
        goal.setdefault("goal_id", new_id("goal"))
        goal.setdefault("created_at", datetime.now(UTC).isoformat())
        if goal["version"] != 1:
            raise GoalMutationError("create() must start at version 1")
        goal.pop("content_hash", None)
        goal["content_hash"] = content_hash(_hashable_goal(goal))
        validate(goal, "goal_contract.schema.json")
        gid = goal["goal_id"]
        if gid in self._versions:
            raise GoalMutationError(f"goal already exists: {gid}")
        self._versions[gid] = [deepcopy(goal)]
        self._ledger.append(
            event_type="goal.created",
            tenant_id=goal["tenant_id"],
            workspace_id=goal["workspace_id"],
            goal_id=gid,
            payload={"goal_id": gid, "version": 1, "content_hash": goal["content_hash"]},
            producer="runtime.goals",
        )
        return deepcopy(goal)

    def get(self, goal_id: str, version: int | None = None) -> dict[str, Any]:
        versions = self._versions.get(goal_id)
        if not versions:
            raise GoalNotFoundError(goal_id)
        if version is None:
            return deepcopy(versions[-1])
        if version < 1 or version > len(versions):
            raise GoalNotFoundError(f"{goal_id}@v{version}")
        return deepcopy(versions[version - 1])

    def amend(
        self,
        goal_id: str,
        *,
        changes: dict[str, Any],
        proposer: str,
        reason: str,
        changed_fields: list[str],
        authority_ref: str | None = None,
        approval_ref: str | None = None,
        impact_analysis: str | None = None,
    ) -> dict[str, Any]:
        current = self.get(goal_id)
        # Prove immutability of prior version by keeping identity of stored object
        prior = self._versions[goal_id][-1]
        prior_hash = prior["content_hash"]

        new_goal = deepcopy(current)
        for key, value in changes.items():
            if key in {"goal_id", "version", "schema_version", "content_hash", "created_at"}:
                raise GoalMutationError(f"cannot amend immutable field: {key}")
            new_goal[key] = deepcopy(value)

        new_goal["version"] = current["version"] + 1
        new_goal["supersedes_version"] = current["version"]
        new_goal["amendment"] = {
            "proposer": proposer,
            "reason": reason,
            "changed_fields": list(changed_fields),
            "authority_ref": authority_ref,
            "approval_ref": approval_ref,
            "impact_analysis": impact_analysis,
        }
        # Drop None optional amendment fields
        new_goal["amendment"] = {k: v for k, v in new_goal["amendment"].items() if v is not None}
        new_goal.pop("content_hash", None)
        new_goal["content_hash"] = content_hash(_hashable_goal(new_goal))
        validate(new_goal, "goal_contract.schema.json")

        # Prior version must remain byte-identical
        if self._versions[goal_id][-1]["content_hash"] != prior_hash:
            raise GoalMutationError("prior goal version was mutated — integrity failure")

        self._versions[goal_id].append(deepcopy(new_goal))
        self._ledger.append(
            event_type="goal.amended",
            tenant_id=new_goal["tenant_id"],
            workspace_id=new_goal["workspace_id"],
            goal_id=goal_id,
            payload={
                "goal_id": goal_id,
                "from_version": current["version"],
                "to_version": new_goal["version"],
                "changed_fields": changed_fields,
                "content_hash": new_goal["content_hash"],
            },
            producer="runtime.goals",
            principal_id=proposer,
        )
        return deepcopy(new_goal)

    def overwrite_forbidden(self, goal_id: str, _new: dict[str, Any]) -> None:
        raise GoalMutationError("Goal cannot be overwritten; use amend() (GOS-I06)")


def _hashable_goal(goal: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in goal.items() if k != "content_hash"}
