"""Ephemeral cognitive workers — created for a task, destroyed after."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from global_os.common.hashing import new_id
from global_os.runtime.events.ledger import EventLedger
from global_os.world.artifacts import ArtifactStore

WorkerFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class WorkerSpec:
    mission: str
    capabilities: frozenset[str]
    parent_capabilities: frozenset[str]
    fn: WorkerFn


@dataclass
class WorkerResult:
    worker_id: str
    mission: str
    artifact_digest: str | None
    output: dict[str, Any]
    destroyed: bool = True


@dataclass
class WorkerRuntime:
    ledger: EventLedger
    artifacts: ArtifactStore
    _active: dict[str, WorkerSpec] = field(default_factory=dict)

    def spawn(
        self,
        spec: WorkerSpec,
        *,
        tenant_id: str,
        workspace_id: str,
        goal_id: str,
    ) -> str:
        if not spec.capabilities.issubset(spec.parent_capabilities):
            raise ValueError("worker capabilities must be ⊆ parent (GOS-I04)")
        worker_id = new_id("wkr")
        self._active[worker_id] = spec
        self.ledger.append(
            event_type="task.transitioned",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            principal_id=worker_id,
            payload={"worker_id": worker_id, "mission": spec.mission, "state": "SPAWNED"},
            producer="cognition.workers",
        )
        return worker_id

    def run(
        self,
        worker_id: str,
        assignment: dict[str, Any],
        *,
        tenant_id: str,
        workspace_id: str,
        goal_id: str,
    ) -> WorkerResult:
        spec = self._active[worker_id]
        output = spec.fn(assignment)
        ref = self.artifacts.put_json(
            {"worker_id": worker_id, "mission": spec.mission, "output": output}
        )
        self.ledger.append(
            event_type="task.transitioned",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            principal_id=worker_id,
            payload={
                "worker_id": worker_id,
                "state": "COMPLETED",
                "artifact_digest": ref.digest,
            },
            producer="cognition.workers",
        )
        # ephemeral: destroy persona, keep artifact
        del self._active[worker_id]
        return WorkerResult(
            worker_id=worker_id,
            mission=spec.mission,
            artifact_digest=ref.digest,
            output=output,
            destroyed=True,
        )
