"""Organizational units and manager-workers topology compiler v0."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class OrganizationError(Exception):
    pass


class OrganizationCompiler:
    """v0: manager_workers from Goal Contract capabilities + task titles."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._units: dict[str, dict[str, Any]] = {}

    def compile_manager_workers(
        self,
        goal: dict[str, Any],
        *,
        worker_missions: list[str],
        budget_usd: float,
        budget_tokens: int,
    ) -> dict[str, Any]:
        if not worker_missions:
            raise OrganizationError("manager_workers requires at least one worker mission")

        goal_caps = list(goal["authority"]["capabilities"])
        parent_id = new_id("org")
        parent = {
            "id": parent_id,
            "schema_version": "0.1.0",
            "goal_id": goal["goal_id"],
            "mission": f"Manage goal {goal['goal_id']}",
            "parent": None,
            "children": [],
            "inputs": ["goal_contract"],
            "output_contract": "integrated_verified_result",
            "authority": {"capabilities": goal_caps},
            "budget": {"usd": budget_usd, "tokens": budget_tokens},
            "state": "ACTIVE",
            "required_independence": False,
            "artifact_namespace": f"artifacts/{goal['goal_id']}/manager",
        }
        validate(parent, "org_unit.schema.json")
        self._units[parent_id] = parent

        per_usd = budget_usd / len(worker_missions)
        per_tokens = budget_tokens // len(worker_missions)
        children: list[str] = []
        for mission in worker_missions:
            child_id = new_id("org")
            # workers get subset — never expand (GOS-I04)
            child_caps = [c for c in goal_caps if not c.endswith(".send") and "payment" not in c]
            child = {
                "id": child_id,
                "schema_version": "0.1.0",
                "goal_id": goal["goal_id"],
                "mission": mission,
                "parent": parent_id,
                "children": [],
                "inputs": ["task_assignment"],
                "output_contract": "artifact_and_evidence",
                "authority": {"capabilities": child_caps},
                "budget": {"usd": per_usd, "tokens": per_tokens},
                "state": "PLANNED",
                "required_independence": False,
                "artifact_namespace": f"artifacts/{goal['goal_id']}/{child_id}",
            }
            validate(child, "org_unit.schema.json")
            if not set(child_caps).issubset(set(goal_caps)):
                raise OrganizationError("child authority must be ⊆ parent")
            self._units[child_id] = child
            children.append(child_id)

        parent["children"] = children
        self._units[parent_id] = parent
        return {
            "topology": "manager_workers",
            "parent": deepcopy(parent),
            "workers": [deepcopy(self._units[c]) for c in children],
        }

    def get(self, org_id: str) -> dict[str, Any]:
        return deepcopy(self._units[org_id])
