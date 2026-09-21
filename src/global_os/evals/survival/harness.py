"""Runtime survival injection harness — honest fidelity only when exercised."""

from __future__ import annotations

from typing import Any

from global_os.adapters.storage import connect_sqlite
from global_os.common.hashing import content_hash, new_id
from global_os.epistemic import EpistemicStore
from global_os.evals.survival.scenarios import (
    DEFAULT_SCENARIOS,
    Injection,
    ScenarioFidelity,
    SurvivalReport,
    SurvivalScenario,
)
from global_os.kernel.action_gateway.gateway import ToolGateway, ToolResult
from global_os.kernel.budget.kernel import BudgetExhausted, BudgetKernel, BudgetLimits
from global_os.runtime.events.ledger import EventLedger
from global_os.runtime.workflows import DurableRunner, WorkflowAborted, goal_execution_workflow
from global_os.verification import EvidenceCandidatePipeline


def _run_process_kill() -> SurvivalScenario:
    conn = connect_sqlite(":memory:")
    runner = DurableRunner(conn)
    wf = goal_execution_workflow()
    run_id = "surv_mid_task_kill"
    try:
        runner.start_or_resume(run_id, wf, {}, kill_after_step="plan")
        aborted = False
    except WorkflowAborted:
        aborted = True
    final = DurableRunner(conn).start_or_resume(run_id, wf, {})
    passed = aborted and final.get("phase") == "reported"
    return SurvivalScenario(
        "mid_task_kill",
        [Injection.PROCESS_KILL],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="DurableRunner abort/resume",
    )


def _run_false_tool_success() -> SurvivalScenario:
    """Tool success ≠ world effect; discrepancy must surface (GOS-I13/I22)."""
    ledger = EventLedger()
    gateway = ToolGateway(ledger)
    calls = {"n": 0}

    def lying_tool(_proposal: dict[str, Any]) -> ToolResult:
        calls["n"] += 1
        return ToolResult(success=True, payload={"claimed": "paid"})

    gateway.register_tool("payment.fake", lying_tool)
    token = new_id("tok")
    gateway.accept_token(token)
    receipt = gateway.execute(
        tool_id="payment.fake",
        proposal={
            "idempotency_key": "idem_false_1",
            "goal_id": "goal_surv",
            "principal_id": "wkr_1",
        },
        execution_token=token,
        tenant_id="t",
        workspace_id="w",
        intended_effect="invoice_paid",
        observation={"effect": "invoice_still_unpaid"},
    )
    epi = EpistemicStore(ledger)
    pipe = EvidenceCandidatePipeline(ledger, epi)
    cand = pipe.ingest_execution_trace(
        goal_id="goal_surv",
        origin="tool_result",
        payload={"tool": "payment.fake", "receipt": receipt},
        tenant_id="t",
        workspace_id="w",
        tool_name="payment.fake",
        summary="tool claimed success",
    )
    passed = (
        receipt["tool_response"]["success"] is True
        and receipt["discrepancy"] != "none"
        and cand["status"] == "CANDIDATE"
        and calls["n"] == 1
    )
    return SurvivalScenario(
        "false_success",
        [Injection.FALSE_TOOL_SUCCESS],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="EffectReceipt discrepancy + EvidenceCandidate remains CANDIDATE",
    )


def _run_duplicate_action() -> SurvivalScenario:
    ledger = EventLedger()
    gateway = ToolGateway(ledger)
    calls = {"n": 0}

    def once(_proposal: dict[str, Any]) -> ToolResult:
        calls["n"] += 1
        return ToolResult(success=True, payload={"side_effect": 1})

    gateway.register_tool("side.effect", once)
    proposal = {
        "idempotency_key": "idem_dup_1",
        "goal_id": "goal_surv",
        "principal_id": "wkr_1",
    }
    t1, t2 = new_id("tok"), new_id("tok")
    gateway.accept_token(t1)
    gateway.accept_token(t2)
    r1 = gateway.execute(
        tool_id="side.effect",
        proposal=proposal,
        execution_token=t1,
        tenant_id="t",
        workspace_id="w",
        intended_effect="done",
        observation={"effect": "done"},
    )
    r2 = gateway.execute(
        tool_id="side.effect",
        proposal=proposal,
        execution_token=t2,
        tenant_id="t",
        workspace_id="w",
        intended_effect="done",
        observation={"effect": "done"},
    )
    passed = calls["n"] == 1 and r1["receipt_id"] == r2["receipt_id"]
    return SurvivalScenario(
        "dup_effect",
        [Injection.DUPLICATE_ACTION],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="ToolGateway idempotency prevents duplicate material handler calls",
    )


def _run_source_invalidation() -> SurvivalScenario:
    from datetime import UTC, datetime

    ledger = EventLedger()
    epi = EpistemicStore(ledger)
    now = datetime.now(UTC).isoformat()
    digest = content_hash({"body": "lead time 90d"})
    epi.put_evidence(
        {
            "evidence_id": "ev_surv",
            "schema_version": "0.1.0",
            "goal_id": "goal_surv",
            "status": "SOURCE_CONTENT_VERIFIED",
            "trust_label": "EXTERNAL_UNTRUSTED",
            "recorded_at": now,
            "known_at": now,
            "content_digest": digest,
        }
    )
    epi.put_claim(
        {
            "claim_id": "cl_surv",
            "schema_version": "0.1.0",
            "goal_id": "goal_surv",
            "statement": "Lead time is 90 days",
            "status": "ACTIVE",
            "evidence_ids": ["ev_surv"],
            "confidence": "MEDIUM",
            "confidence_basis": "single source",
            "recorded_at": now,
        }
    )
    result = epi.invalidate_evidence(
        "ev_surv", tenant_id="t", workspace_id="w", reason="source withdrawn mid-run"
    )
    passed = (
        result["claims"] == ["cl_surv"]
        and epi.get_claim("cl_surv")["status"] == "STALE"
        and epi.get_evidence("ev_surv")["status"] == "INVALIDATED"
    )
    return SurvivalScenario(
        "stale_source",
        [Injection.SOURCE_INVALIDATION],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="EpistemicStore invalidation propagates to dependent claim",
    )


def _run_budget_reduction() -> SurvivalScenario:
    ledger = EventLedger()
    budget = BudgetKernel(
        ledger,
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_surv",
        limits=BudgetLimits(usd=10.0, tokens=10_000, api_calls=100, wall_time_seconds=3600, agent_count=4),
    )
    budget.reserve("r1", usd=3.0)
    budget.commit("r1")
    # Mid-run budget cut below remaining headroom for next reservation
    budget.limits = BudgetLimits(
        usd=3.5, tokens=10_000, api_calls=100, wall_time_seconds=3600, agent_count=4
    )
    blocked = False
    try:
        budget.reserve("r2", usd=1.0)
    except BudgetExhausted:
        blocked = True
    passed = blocked and budget.usage.usd == 3.0
    return SurvivalScenario(
        "budget_cut",
        [Injection.BUDGET_REDUCTION],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="BudgetKernel rejects spend after mid-run limit reduction",
    )


def _run_api_outage() -> SurvivalScenario:
    from global_os.adapters.models import GenerateRequest, ModelProviderError, OutageModelProvider
    from global_os.memory import NullResultStore

    ledger = EventLedger()
    nulls = NullResultStore(ledger)
    provider = OutageModelProvider()
    fabricated = False
    recorded = False
    try:
        provider.generate(GenerateRequest(prompt="continue the goal"))
        fabricated = True
    except ModelProviderError as exc:
        nulls.record(
            attempt="model.generate",
            why_failed=str(exc),
            evidence=["provider_exception"],
            conditions="api_outage",
            reopen_condition="provider_health_ok",
            tenant_id="t",
            workspace_id="w",
            goal_id="goal_surv",
        )
        recorded = True
    passed = recorded and not fabricated and len(nulls.list_all()) == 1
    return SurvivalScenario(
        "api_outage",
        [Injection.API_OUTAGE],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="Model outage recorded as null result; no fabricated success",
    )


def _run_model_swap() -> SurvivalScenario:
    from global_os.adapters.models import (
        EchoModelProvider,
        GenerateRequest,
        ModelRef,
        SwappableModelProvider,
    )
    from global_os.cognition.metareasoning import ReasoningBudgetController

    swap = SwappableModelProvider(EchoModelProvider())
    first = swap.generate(GenerateRequest(prompt="step-1"))
    # Mid-run swap to another stub family

    class OtherEcho(EchoModelProvider):
        def generate(self, request: GenerateRequest) -> Any:
            resp = super().generate(request)
            return type(resp)(
                text=resp.text,
                model=ModelRef("stub", "echo-b", "1"),
                input_tokens=resp.input_tokens,
                output_tokens=resp.output_tokens,
            )

    verification_tier = 2
    ctrl = ReasoningBudgetController()
    before = ctrl.decide(
        {"default_effort": "medium", "increase_when": [], "decrease_when": ["confidence_high"]},
        verification_tier=verification_tier,
        signals={"confidence_high"},
    )
    swap.swap(OtherEcho())
    second = swap.generate(GenerateRequest(prompt="step-2"))
    after = ctrl.decide(
        {"default_effort": "medium", "increase_when": [], "decrease_when": ["confidence_high"]},
        verification_tier=verification_tier,
        signals={"confidence_high"},
    )
    passed = (
        swap.swap_count == 1
        and first.model.model != second.model.model
        and before.verification_tier_unchanged == verification_tier
        and after.verification_tier_unchanged == verification_tier
    )
    return SurvivalScenario(
        "model_swap",
        [Injection.MODEL_SWAP],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="Mid-run model swap does not change verification tier (GOS-I23)",
    )


def _run_slow_dependency() -> SurvivalScenario:
    from global_os.adapters.models import GenerateRequest, ModelProviderError, SlowModelProvider
    from global_os.memory import NullResultStore
    from global_os.world.sandbox import Sandbox, SandboxLimits

    ledger = EventLedger()
    nulls = NullResultStore(ledger)
    slow = SlowModelProvider(delay_seconds=5.0, budget_seconds=0.01)
    timed_out_model = False
    try:
        slow.generate(GenerateRequest(prompt="long"))
    except ModelProviderError:
        timed_out_model = True
        nulls.record(
            attempt="model.generate.slow",
            why_failed="slow_dependency",
            evidence=["wall_budget_exceeded"],
            conditions="dependency_latency",
            reopen_condition="latency_ok",
            tenant_id="t",
            workspace_id="w",
            goal_id="goal_surv",
        )
    sb = Sandbox(SandboxLimits(walltime_seconds=0.05))
    sb.create()
    try:
        result = sb.execute(["sleep", "2"])
        sandbox_timed = result.timed_out is True
    finally:
        sb.destroy()
    passed = timed_out_model and sandbox_timed and len(nulls.list_all()) == 1
    return SurvivalScenario(
        "slow_dependency",
        [Injection.SLOW_DEPENDENCY],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="Slow provider exceeds wall budget → fail-closed timeout",
    )


def _run_constraint_change() -> SurvivalScenario:
    from global_os.runtime.goals import GoalStore

    ledger = EventLedger()
    goals = GoalStore(ledger)
    goal = goals.create(
        {
            "schema_version": "0.1.0",
            "goal_id": "goal_surv_constraint",
            "version": 1,
            "tenant_id": "t",
            "workspace_id": "w",
            "objective": {"text": "do the thing"},
            "success_criteria": [{"id": "sc", "description": "done"}],
            "invariants": ["read_only"],
            "non_goals": [],
            "forbidden_outcomes": [],
            "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
            "authority": {"delegation_depth_max": 1, "capabilities": ["filesystem.read"]},
            "evidence_requirements": {},
            "termination": ["success_criteria_met"],
            "created_at": "2026-09-21T00:00:00+00:00",
        }
    )
    v1 = goals.get(goal["goal_id"], version=1)
    amended = goals.amend(
        goal["goal_id"],
        changes={"invariants": ["read_only", "no_network"]},
        proposer="human",
        reason="constraint_change mid-run",
        changed_fields=["invariants"],
    )
    v1_again = goals.get(goal["goal_id"], version=1)
    passed = (
        v1["version"] == 1
        and amended["version"] == 2
        and v1_again["invariants"] == ["read_only"]
        and amended["invariants"] == ["read_only", "no_network"]
        and v1_again == v1
    )
    return SurvivalScenario(
        "constraint_change",
        [Injection.CONSTRAINT_CHANGE],
        ScenarioFidelity.RUNTIME_INJECTED,
        passed=passed,
        notes="Goal amend creates new version; v1 immutable (GOS-I06)",
    )


_INJECTION_RUNNERS: dict[Injection, Any] = {
    Injection.PROCESS_KILL: _run_process_kill,
    Injection.FALSE_TOOL_SUCCESS: _run_false_tool_success,
    Injection.DUPLICATE_ACTION: _run_duplicate_action,
    Injection.SOURCE_INVALIDATION: _run_source_invalidation,
    Injection.BUDGET_REDUCTION: _run_budget_reduction,
    Injection.API_OUTAGE: _run_api_outage,
    Injection.MODEL_SWAP: _run_model_swap,
    Injection.SLOW_DEPENDENCY: _run_slow_dependency,
    Injection.CONSTRAINT_CHANGE: _run_constraint_change,
}


def run_survival_suite(
    scenarios: list[SurvivalScenario] | None = None,
) -> SurvivalReport:
    """Execute DEFAULT (or provided) scenarios with honest fidelity labels."""
    results: list[SurvivalScenario] = []
    for base in scenarios or DEFAULT_SCENARIOS:
        if base.fidelity != ScenarioFidelity.RUNTIME_INJECTED:
            results.append(
                SurvivalScenario(
                    base.name,
                    list(base.injections),
                    ScenarioFidelity.STUB,
                    passed=None,
                    notes=f"stub; {base.notes}",
                )
            )
            continue
        if len(base.injections) != 1:
            raise ValueError(f"harness expects single injection per scenario: {base.name}")
        injection = base.injections[0]
        runner = _INJECTION_RUNNERS.get(injection)
        if runner is None:
            results.append(
                SurvivalScenario(
                    base.name,
                    list(base.injections),
                    ScenarioFidelity.STUB,
                    passed=None,
                    notes=f"no runtime runner for {injection.value}",
                )
            )
            continue
        results.append(runner())
    return SurvivalReport(scenarios=results)
