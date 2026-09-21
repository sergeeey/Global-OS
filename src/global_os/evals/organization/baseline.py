"""H-ORG-001 baseline: single_solver vs manager_workers (synthetic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.cognition.organization import OrganizationCompiler
from global_os.runtime.events import EventLedger


@dataclass(frozen=True)
class TopologyResult:
    topology: str
    task_count: int
    org_units: int
    coordination_edges: int
    duplicate_work: int
    success: bool
    cost_units: float


def run_single_solver(goal_id: str, task_count: int | None = None) -> TopologyResult:
    tasks = build_repo_audit_dag(goal_id)
    n = task_count or len(tasks)
    # Single agent: no coordination, but serial cost grows linearly
    return TopologyResult(
        topology="single_solver",
        task_count=n,
        org_units=1,
        coordination_edges=0,
        duplicate_work=0,
        success=True,
        cost_units=float(n) * 1.0,
    )


def run_manager_workers(
    goal: dict[str, Any], worker_missions: list[str] | None = None
) -> TopologyResult:
    ledger = EventLedger()
    org = OrganizationCompiler(ledger)
    missions = worker_missions or ["architecture", "testing", "verification", "report"]
    graph = org.compile_manager_workers(
        goal,
        worker_missions=missions,
        budget_usd=10.0,
        budget_tokens=10_000,
    )
    tasks = build_repo_audit_dag(goal["goal_id"])
    # manager + workers; coordination edges = workers; slight overhead
    workers = len(graph["workers"])
    return TopologyResult(
        topology="manager_workers",
        task_count=len(tasks),
        org_units=1 + workers,
        coordination_edges=workers,
        duplicate_work=0,
        success=True,
        cost_units=float(len(tasks)) * 0.85 + float(workers) * 0.2,
    )


def compare_baselines(goal: dict[str, Any]) -> dict[str, TopologyResult]:
    return {
        "single_solver": run_single_solver(goal["goal_id"]),
        "manager_workers": run_manager_workers(goal),
    }
