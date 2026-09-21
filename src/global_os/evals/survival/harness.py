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


_INJECTION_RUNNERS: dict[Injection, Any] = {
    Injection.PROCESS_KILL: _run_process_kill,
    Injection.FALSE_TOOL_SUCCESS: _run_false_tool_success,
    Injection.DUPLICATE_ACTION: _run_duplicate_action,
    Injection.SOURCE_INVALIDATION: _run_source_invalidation,
    Injection.BUDGET_REDUCTION: _run_budget_reduction,
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
