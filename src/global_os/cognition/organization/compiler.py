"""Organizational units and topology compiler (DCO P0 contracts; GOS-I30)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.cognition.organization.topology import (
    IMPLEMENTED_TOPOLOGIES,
    OrganizationTopology,
)
from global_os.common.hashing import new_id
from global_os.contracts.validate import validate
from global_os.runtime.events.ledger import EventLedger


class OrganizationError(Exception):
    pass


class OrganizationCompiler:
    """Compile OrganizationGraph. Topology enum is P0; optimality is P1."""

    def __init__(self, ledger: EventLedger) -> None:
        self._ledger = ledger
        self._units: dict[str, dict[str, Any]] = {}

    def compile(
        self,
        goal: dict[str, Any],
        *,
        topology: OrganizationTopology | str,
        worker_missions: list[str] | None = None,
        budget_usd: float = 10.0,
        budget_tokens: int = 10_000,
    ) -> dict[str, Any]:
        topo = (
            topology
            if isinstance(topology, OrganizationTopology)
            else OrganizationTopology(topology)
        )
        if topo not in IMPLEMENTED_TOPOLOGIES:
            raise OrganizationError(
                f"topology {topo.value!r} is CONTRACTED (enum P0); "
                "compiler not implemented — refusing silent manager_workers fallback (GOS-I30)"
            )
        if topo == OrganizationTopology.SINGLE_SOLVER:
            return self._compile_single(goal, budget_usd=budget_usd, budget_tokens=budget_tokens)
        if topo == OrganizationTopology.PARALLEL_WORKERS:
            missions = worker_missions or ["worker_a", "worker_b"]
            return self._compile_parallel(
                goal, worker_missions=missions, budget_usd=budget_usd, budget_tokens=budget_tokens
            )
        # manager_workers
        missions = worker_missions or ["architecture", "testing", "verification"]
        return self.compile_manager_workers(
            goal,
            worker_missions=missions,
            budget_usd=budget_usd,
            budget_tokens=budget_tokens,
        )

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
        units = [deepcopy(parent)] + [deepcopy(self._units[c]) for c in children]
        return self._graph(
            goal_id=goal["goal_id"],
            topology=OrganizationTopology.MANAGER_WORKERS,
            units=units,
            legacy_parent=deepcopy(parent),
            legacy_workers=[deepcopy(self._units[c]) for c in children],
        )

    def _compile_single(
        self, goal: dict[str, Any], *, budget_usd: float, budget_tokens: int
    ) -> dict[str, Any]:
        goal_caps = list(goal["authority"]["capabilities"])
        unit_id = new_id("org")
        unit = {
            "id": unit_id,
            "schema_version": "0.1.0",
            "goal_id": goal["goal_id"],
            "mission": f"Solve goal {goal['goal_id']} as single solver",
            "parent": None,
            "children": [],
            "inputs": ["goal_contract"],
            "output_contract": "artifact_and_evidence",
            "authority": {"capabilities": goal_caps},
            "budget": {"usd": budget_usd, "tokens": budget_tokens},
            "state": "ACTIVE",
            "required_independence": False,
            "artifact_namespace": f"artifacts/{goal['goal_id']}/single",
        }
        validate(unit, "org_unit.schema.json")
        self._units[unit_id] = unit
        return self._graph(
            goal_id=goal["goal_id"],
            topology=OrganizationTopology.SINGLE_SOLVER,
            units=[deepcopy(unit)],
            legacy_parent=deepcopy(unit),
            legacy_workers=[],
        )

    def _compile_parallel(
        self,
        goal: dict[str, Any],
        *,
        worker_missions: list[str],
        budget_usd: float,
        budget_tokens: int,
    ) -> dict[str, Any]:
        if len(worker_missions) < 2:
            raise OrganizationError("parallel_workers requires ≥2 missions")
        goal_caps = list(goal["authority"]["capabilities"])
        per_usd = budget_usd / len(worker_missions)
        per_tokens = budget_tokens // len(worker_missions)
        units: list[dict[str, Any]] = []
        for mission in worker_missions:
            uid = new_id("org")
            child_caps = [c for c in goal_caps if not c.endswith(".send") and "payment" not in c]
            unit = {
                "id": uid,
                "schema_version": "0.1.0",
                "goal_id": goal["goal_id"],
                "mission": mission,
                "parent": None,
                "children": [],
                "inputs": ["goal_contract"],
                "output_contract": "artifact_and_evidence",
                "authority": {"capabilities": child_caps},
                "budget": {"usd": per_usd, "tokens": per_tokens},
                "state": "PLANNED",
                "required_independence": True,
                "artifact_namespace": f"artifacts/{goal['goal_id']}/{uid}",
            }
            validate(unit, "org_unit.schema.json")
            self._units[uid] = unit
            units.append(deepcopy(unit))
        return self._graph(
            goal_id=goal["goal_id"],
            topology=OrganizationTopology.PARALLEL_WORKERS,
            units=units,
            legacy_parent=None,
            legacy_workers=units,
        )

    def _graph(
        self,
        *,
        goal_id: str,
        topology: OrganizationTopology,
        units: list[dict[str, Any]],
        legacy_parent: dict[str, Any] | None,
        legacy_workers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        graph: dict[str, Any] = {
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "topology": topology.value,
            "units": units,
            # Never claim measured superiority from compile alone (GOS-I30).
            "hypothesis_status": "UNPROVEN",
            "notes": (
                "Topology selected as compile choice only; "
                "H-ORG superiority remains experimental P1"
            ),
            # Back-compat keys used by existing tests/callers
            "parent": legacy_parent,
            "workers": legacy_workers,
        }
        # Validate core fields without legacy extras
        core = {
            "schema_version": graph["schema_version"],
            "goal_id": graph["goal_id"],
            "topology": graph["topology"],
            "units": graph["units"],
            "hypothesis_status": graph["hypothesis_status"],
            "notes": graph["notes"],
        }
        validate(core, "organization_graph.schema.json")
        return graph

    def get(self, org_id: str) -> dict[str, Any]:
        return deepcopy(self._units[org_id])
