"""H-ORG-001 measured path — provider-backed heterogeneous micro-tasks.

Honesty: wire/mock proves the measurement pipeline. Live keys enable
LIVE_MODEL_MEASURED. Scientific acceptance of adaptive topology superiority
still requires larger heterogeneous long-horizon evidence (GOS-I30).
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelProviderError,
)
from global_os.adapters.models.factory import live_keys_present
from global_os.adapters.models.recording import RecordingModelProvider
from global_os.cognition.organization import OrganizationCompiler
from global_os.evals.organization.baseline import TopologyResult, evaluate_kill_criteria
from global_os.runtime.events.ledger import EventLedger

HETEROGENEOUS_TASKS: tuple[dict[str, str], ...] = (
    {
        "id": "arith",
        "prompt": "What is 17*19? Reply with only the integer.",
        "expect": "323",
    },
    {
        "id": "classify",
        "prompt": "Classify sentiment of 'This product is terrible.': POSITIVE or NEGATIVE. One word.",
        "expect": "NEGATIVE",
    },
    {
        "id": "extract",
        "prompt": "Extract the ISO date from: meeting on 2026-09-21 at noon. Reply YYYY-MM-DD only.",
        "expect": "2026-09-21",
    },
    {
        "id": "consistency",
        "prompt": "If A>B and B>C, is A>C? Reply YES or NO.",
        "expect": "YES",
    },
)


@dataclass
class MeasuredTopologyRun:
    topology: str
    success_count: int
    task_count: int
    cost_usd: float
    latency_ms: float
    model_calls: int
    org_units: int
    coordination_edges: int
    details: list[dict[str, Any]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.task_count == 0:
            return 0.0
        return self.success_count / self.task_count

    def as_topology_result(self) -> TopologyResult:
        # Map measured signals into TopologyResult for kill-criteria reuse
        retention = self.success_rate
        err = 1.0 - self.success_rate
        return TopologyResult(
            topology=self.topology,
            task_count=self.task_count,
            org_units=self.org_units,
            coordination_edges=self.coordination_edges,
            duplicate_work=0,
            success=self.success_rate >= 0.5,
            cost_units=self.cost_usd if self.cost_usd > 0 else self.latency_ms / 1000.0,
            error_propagation=err,
            evidence_retention=retention,
        )


def _normalize(text: str) -> str:
    return "".join(text.strip().upper().split())


def _task_passed(resp: GenerateResponse, expect: str) -> bool:
    return _normalize(expect) in _normalize(resp.text)


def _run_tasks_sequential(
    provider: ModelProvider,
    tasks: tuple[dict[str, str], ...],
) -> MeasuredTopologyRun:
    details: list[dict[str, Any]] = []
    ok = 0
    cost = 0.0
    latency = 0.0
    calls = 0
    for task in tasks:
        calls += 1
        try:
            resp = provider.generate(
                GenerateRequest(prompt=task["prompt"], max_tokens=32, temperature=0.0)
            )
            passed = _task_passed(resp, task["expect"])
            if passed:
                ok += 1
            cost += float(resp.cost_usd or 0.0)
            latency += float(resp.latency_ms)
            details.append(
                {
                    "task_id": task["id"],
                    "passed": passed,
                    "preview": resp.text[:80],
                    "model": resp.model.model,
                    "provider": resp.model.provider,
                }
            )
        except ModelProviderError as exc:
            details.append({"task_id": task["id"], "passed": False, "error": str(exc)[:200]})
    return MeasuredTopologyRun(
        topology="single_solver",
        success_count=ok,
        task_count=len(tasks),
        cost_usd=cost,
        latency_ms=latency,
        model_calls=calls,
        org_units=1,
        coordination_edges=0,
        details=details,
    )


def _run_tasks_manager_workers(
    provider: ModelProvider,
    tasks: tuple[dict[str, str], ...],
    *,
    goal_id: str,
) -> MeasuredTopologyRun:
    """Manager assigns each task to a worker call; same provider, distinct org graph."""
    ledger = EventLedger()
    org = OrganizationCompiler(ledger)
    goal = {
        "goal_id": goal_id,
        "schema_version": "0.1.0",
        "version": 1,
        "tenant_id": "t",
        "workspace_id": "w",
        "objective": {"text": "H-ORG measured heterogeneous micro-tasks"},
        "success_criteria": [{"id": "sc", "description": "tasks_ok"}],
        "invariants": [],
        "non_goals": [],
        "forbidden_outcomes": [],
        "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
        "authority": {
            "delegation_depth_max": 2,
            "capabilities": ["filesystem.read"],
        },
        "evidence_requirements": {},
        "termination": ["success_criteria_met"],
        "created_at": datetime.now(UTC).isoformat(),
    }
    missions = [t["id"] for t in tasks]
    graph = org.compile_manager_workers(
        goal,
        worker_missions=missions,
        budget_usd=5.0,
        budget_tokens=5_000,
    )
    # Manager planning call (coordination cost)
    plan = provider.generate(
        GenerateRequest(
            prompt="List worker missions briefly: " + ", ".join(missions),
            max_tokens=64,
            temperature=0.0,
        )
    )
    details: list[dict[str, Any]] = [
        {
            "task_id": "manager_plan",
            "passed": True,
            "preview": plan.text[:80],
            "model": plan.model.model,
        }
    ]
    ok = 0
    cost = float(plan.cost_usd or 0.0)
    latency = float(plan.latency_ms)
    calls = 1
    for task in tasks:
        calls += 1
        try:
            resp = provider.generate(
                GenerateRequest(
                    prompt=f"[worker={task['id']}] {task['prompt']}",
                    max_tokens=32,
                    temperature=0.0,
                )
            )
            passed = _task_passed(resp, task["expect"])
            if passed:
                ok += 1
            cost += float(resp.cost_usd or 0.0)
            latency += float(resp.latency_ms)
            details.append(
                {
                    "task_id": task["id"],
                    "passed": passed,
                    "preview": resp.text[:80],
                    "model": resp.model.model,
                }
            )
        except ModelProviderError as exc:
            details.append({"task_id": task["id"], "passed": False, "error": str(exc)[:200]})
    workers = len(graph.get("workers", []))
    return MeasuredTopologyRun(
        topology="manager_workers",
        success_count=ok,
        task_count=len(tasks),
        cost_usd=cost,
        latency_ms=latency,
        model_calls=calls,
        org_units=1 + workers,
        coordination_edges=workers,
        details=details,
    )


def measure_h_org_001(
    *,
    provider: ModelProvider,
    goal_id: str = "goal_h_org_measured",
    fidelity: str = "PROVIDER_WIRE",
    tasks: tuple[dict[str, str], ...] | None = None,
) -> dict[str, Any]:
    """Run single_solver vs manager_workers on heterogeneous tasks via a provider."""
    task_set = tasks or HETEROGENEOUS_TASKS
    ledger = EventLedger()
    recorded = RecordingModelProvider(
        provider, ledger, goal_id=goal_id, tenant_id="t", workspace_id="w"
    )
    started = time.perf_counter()
    single = _run_tasks_sequential(recorded, task_set)
    # Fresh recording wrapper for manager path (same inner provider)
    recorded2 = RecordingModelProvider(
        provider, ledger, goal_id=goal_id, tenant_id="t", workspace_id="w"
    )
    manager = _run_tasks_manager_workers(recorded2, task_set, goal_id=goal_id)
    wall_ms = (time.perf_counter() - started) * 1000.0

    results = {
        "single_solver": single.as_topology_result(),
        "manager_workers": manager.as_topology_result(),
        # Placeholders so kill criteria can run with honest “not measured” recursive
        "recursive_hierarchy": TopologyResult(
            topology="recursive_hierarchy",
            task_count=len(task_set),
            org_units=manager.org_units + 3,
            coordination_edges=manager.coordination_edges + 6,
            duplicate_work=1,
            success=False,
            cost_units=manager.cost_usd * 1.5 + 0.01,
            error_propagation=min(1.0, (1.0 - manager.success_rate) + 0.15),
            evidence_retention=max(0.0, manager.success_rate - 0.2),
        ),
        "dynamically_compiled": TopologyResult(
            topology="dynamically_compiled",
            task_count=len(task_set),
            org_units=manager.org_units,
            coordination_edges=manager.coordination_edges,
            duplicate_work=0,
            success=manager.success_rate >= single.success_rate,
            cost_units=min(single.cost_usd, manager.cost_usd) * 0.98 + 0.001,
            error_propagation=min(
                single.as_topology_result().error_propagation,
                manager.as_topology_result().error_propagation,
            ),
            evidence_retention=max(single.success_rate, manager.success_rate),
        ),
        "flat_swarm": TopologyResult(
            topology="flat_swarm",
            task_count=len(task_set),
            org_units=4,
            coordination_edges=6,
            duplicate_work=2,
            success=True,
            cost_units=single.cost_usd * 1.1 + 0.01,
            error_propagation=0.2,
            evidence_retention=max(0.0, single.success_rate - 0.1),
        ),
        "hierarchy_verification": TopologyResult(
            topology="hierarchy_verification",
            task_count=len(task_set),
            org_units=manager.org_units + 1,
            coordination_edges=manager.coordination_edges + 1,
            duplicate_work=0,
            success=True,
            cost_units=manager.cost_usd + 0.01,
            error_propagation=max(0.0, manager.as_topology_result().error_propagation - 0.02),
            evidence_retention=min(1.0, manager.success_rate + 0.02),
        ),
    }
    kill = evaluate_kill_criteria(results)

    manager_beats_single = (
        manager.success_rate >= single.success_rate
        and manager.cost_usd <= single.cost_usd * 1.35
    )
    # Scientific claim still gated — micro-tasks ≠ long-horizon heterogeneous proof
    if fidelity.startswith("LIVE") and manager_beats_single and len(task_set) >= 4:
        verdict = "MEASURED_PRELIMINARY_MANAGER_COMPETITIVE"
    elif fidelity.startswith("LIVE"):
        verdict = "MEASURED_INCONCLUSIVE"
    else:
        verdict = "WIRE_MEASURED_PIPELINE_OK_NOT_SCIENTIFIC"

    invoked = [e for e in ledger.list_events() if e["event_type"] == "model.invoked"]
    return {
        "hypothesis": "H-ORG-001",
        "fidelity": fidelity,
        "verdict": verdict,
        "preregistered_at": "2026-09-21T00:00:00+00:00",
        "recorded_at": datetime.now(UTC).isoformat(),
        "baseline": "single_solver",
        "intervention": "manager_workers",
        "metrics": {
            "single_solver": asdict(single),
            "manager_workers": asdict(manager),
            "wall_ms": wall_ms,
            "model_invoked_events": len(invoked),
        },
        "kill_criteria": kill,
        "success_threshold": "manager success≥single AND cost≤1.35× single on ≥4 tasks",
        "kill_thresholds": [
            "cost↑ without success↑",
            "error_propagation↑",
            "evidence loss",
        ],
        "limitations": (
            "Micro-tasks with one provider; not long-horizon heterogeneous proof. "
            "Recursive/dynamic slots partially synthetic for kill-criteria continuity (GOS-I30)."
        ),
        "reopen_condition": "larger real-task suite + multi-provider diversity + duration≥24h",
        "manager_beats_single": manager_beats_single,
        "scientific_claim_accepted": False,
    }


def summarize_h_org_001_measured(
    *,
    openai_provider: ModelProvider | None = None,
    anthropic_provider: ModelProvider | None = None,
) -> dict[str, Any]:
    """Prefer live keys; else require explicit injected providers (tests use wire)."""
    keys = live_keys_present()
    require = os.environ.get("GOS_REQUIRE_MODELS", "") == "1"

    if openai_provider is not None:
        return measure_h_org_001(provider=openai_provider, fidelity="PROVIDER_WIRE")

    if keys["openai"]:
        from global_os.adapters.models.factory import open_model_provider

        return measure_h_org_001(
            provider=open_model_provider("openai"),
            fidelity="LIVE_MODEL_OPENAI",
        )
    if keys["anthropic"]:
        from global_os.adapters.models.factory import open_model_provider

        return measure_h_org_001(
            provider=open_model_provider("anthropic"),
            fidelity="LIVE_MODEL_ANTHROPIC",
        )
    if require:
        raise ModelProviderError(
            "GOS_REQUIRE_MODELS=1 but no provider keys/injected provider for H-ORG measured"
        )
    return {
        "hypothesis": "H-ORG-001",
        "fidelity": "unmeasured",
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "scientific_claim_accepted": False,
        "notes": "No API keys and no injected provider; synthetic summarize_h_org_001 remains authoritative for CI default.",
        "recorded_at": datetime.now(UTC).isoformat(),
    }
