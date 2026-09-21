"""H-ORG-001 organizational topology benchmark (synthetic).

Fidelity: synthetic_deterministic. Does NOT accept/reject the scientific
hypothesis until real-model heterogeneous long tasks are measured.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
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
    error_propagation: float
    evidence_retention: float


def run_single_solver(goal_id: str, task_count: int | None = None) -> TopologyResult:
    tasks = build_repo_audit_dag(goal_id)
    n = task_count or len(tasks)
    return TopologyResult(
        topology="single_solver",
        task_count=n,
        org_units=1,
        coordination_edges=0,
        duplicate_work=0,
        success=True,
        cost_units=float(n) * 1.0,
        error_propagation=0.05,
        evidence_retention=0.95,
    )


def run_flat_swarm(goal_id: str, agents: int = 4) -> TopologyResult:
    tasks = build_repo_audit_dag(goal_id)
    n = len(tasks)
    # Parallelism helps cost; duplicate exploration rises without manager.
    return TopologyResult(
        topology="flat_swarm",
        task_count=n,
        org_units=agents,
        coordination_edges=agents * (agents - 1) // 2,
        duplicate_work=max(0, agents - 2),
        success=True,
        cost_units=float(n) * 0.7 + float(agents) * 0.35,
        error_propagation=0.18,
        evidence_retention=0.7,
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
    workers = len(graph["workers"])
    return TopologyResult(
        topology="manager_workers",
        task_count=len(tasks),
        org_units=1 + workers,
        coordination_edges=workers,
        duplicate_work=0,
        success=True,
        cost_units=float(len(tasks)) * 0.85 + float(workers) * 0.2,
        error_propagation=0.08,
        evidence_retention=0.88,
    )


def run_recursive_hierarchy(goal: dict[str, Any]) -> TopologyResult:
    """Synthetic recursive org — often fails kill criteria on management cost."""
    base = run_manager_workers(goal)
    # Extra management layer: more units/edges, higher cost, evidence loss in summaries
    return TopologyResult(
        topology="recursive_hierarchy",
        task_count=base.task_count,
        org_units=base.org_units + 3,
        coordination_edges=base.coordination_edges + 6,
        duplicate_work=1,
        success=True,
        cost_units=base.cost_units * 1.45,
        error_propagation=0.22,
        evidence_retention=0.55,
    )


def run_hierarchy_with_verification(goal: dict[str, Any]) -> TopologyResult:
    base = run_manager_workers(goal)
    return TopologyResult(
        topology="hierarchy_verification",
        task_count=base.task_count,
        org_units=base.org_units + 1,  # verifier unit
        coordination_edges=base.coordination_edges + 1,
        duplicate_work=0,
        success=True,
        cost_units=base.cost_units + 0.4,
        error_propagation=0.04,
        evidence_retention=0.93,
    )


def run_dynamically_compiled(goal: dict[str, Any]) -> TopologyResult:
    """Dynamic org via OrganizationCompiler — preferred when it beats fixed topologies."""
    base = run_manager_workers(goal)
    return TopologyResult(
        topology="dynamically_compiled",
        task_count=base.task_count,
        org_units=base.org_units,
        coordination_edges=base.coordination_edges,
        duplicate_work=0,
        success=True,
        cost_units=base.cost_units * 0.95,
        error_propagation=0.06,
        evidence_retention=0.9,
    )


def compare_baselines(goal: dict[str, Any]) -> dict[str, TopologyResult]:
    return {
        "single_solver": run_single_solver(goal["goal_id"]),
        "manager_workers": run_manager_workers(goal),
    }


def compare_all_topologies(goal: dict[str, Any]) -> dict[str, TopologyResult]:
    return {
        "single_solver": run_single_solver(goal["goal_id"]),
        "flat_swarm": run_flat_swarm(goal["goal_id"]),
        "manager_workers": run_manager_workers(goal),
        "recursive_hierarchy": run_recursive_hierarchy(goal),
        "hierarchy_verification": run_hierarchy_with_verification(goal),
        "dynamically_compiled": run_dynamically_compiled(goal),
    }


def evaluate_kill_criteria(results: dict[str, TopologyResult]) -> dict[str, Any]:
    """Apply EVALS.md kill criteria for recursive default (synthetic signals)."""
    single = results["single_solver"]
    manager = results["manager_workers"]
    recursive = results["recursive_hierarchy"]
    dynamic = results["dynamically_compiled"]
    failures: list[str] = []
    if recursive.cost_units >= manager.cost_units * 1.3:
        failures.append("burns_gains_on_management_cost")
    if recursive.error_propagation > manager.error_propagation:
        failures.append("increases_error_propagation")
    if recursive.evidence_retention < manager.evidence_retention:
        failures.append("loses_evidence_in_summaries")
    if recursive.cost_units > single.cost_units and recursive.evidence_retention < single.evidence_retention:
        failures.append("loses_to_single_strong_agent_on_cost_quality")
    if manager.cost_units <= recursive.cost_units and manager.error_propagation <= recursive.error_propagation:
        failures.append("loses_to_manager_worker")
    recursive_default_ok = len(failures) == 0
    preferred = min(
        results.values(),
        key=lambda r: (r.cost_units / max(r.evidence_retention, 0.01), r.error_propagation),
    )
    return {
        "recursive_default_allowed": recursive_default_ok,
        "kill_failures": failures,
        "preferred_topology": preferred.topology,
        "dynamic_beats_fixed_manager": dynamic.cost_units <= manager.cost_units
        and dynamic.evidence_retention >= manager.evidence_retention * 0.98,
    }


def summarize_h_org_001(goal: dict[str, Any] | None = None) -> dict[str, Any]:
    if goal is None:
        goal = {
            "goal_id": "goal_h_org_001",
            "schema_version": "0.1.0",
            "version": 1,
            "title": "H-ORG synthetic",
            "success_criteria": ["synthetic"],
            "constraints": [],
            "budget": {"usd": 10, "tokens": 10000, "time": "1h"},
            "authority_scope": ["filesystem.read"],
            "created_at": datetime.now(UTC).isoformat(),
        }
    results = compare_all_topologies(goal)
    kill = evaluate_kill_criteria(results)
    return {
        "hypothesis": "H-ORG-001",
        "fidelity": "synthetic_deterministic",
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "recorded_at": datetime.now(UTC).isoformat(),
        "topologies": {k: asdict(v) for k, v in results.items()},
        "kill_criteria": kill,
        "notes": (
            "Synthetic topology costs/retention only; do not treat as confirmation "
            "that dynamic org beats fixed topologies on real heterogeneous tasks."
        ),
    }
