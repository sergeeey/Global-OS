"""Survival Benchmark scaffold — honest fidelity labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Injection(str, Enum):
    PROCESS_KILL = "process_kill"
    MODEL_SWAP = "model_swap"
    API_OUTAGE = "api_outage"
    FALSE_TOOL_SUCCESS = "false_tool_success"
    SOURCE_INVALIDATION = "source_invalidation"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    MALICIOUS_DOCUMENT = "malicious_document"
    HUMAN_REJECTION = "human_rejection"
    CONSTRAINT_CHANGE = "constraint_change"
    BUDGET_REDUCTION = "budget_reduction"
    DUPLICATE_ACTION = "duplicate_action"
    CORRUPTED_STATE = "corrupted_state"
    SLOW_DEPENDENCY = "slow_dependency"


class ScenarioFidelity(str, Enum):
    """implemented approximation ≠ fulfilled contract."""

    RUNTIME_INJECTED = "runtime_injected"
    STUB = "stub"


@dataclass
class SurvivalScenario:
    name: str
    injections: list[Injection]
    fidelity: ScenarioFidelity
    duration_hours: float = 24.0
    passed: bool | None = None
    notes: str = ""


@dataclass
class SurvivalReport:
    scenarios: list[SurvivalScenario] = field(default_factory=list)

    @property
    def runtime_scenarios(self) -> list[SurvivalScenario]:
        return [s for s in self.scenarios if s.fidelity == ScenarioFidelity.RUNTIME_INJECTED]

    @property
    def stub_scenarios(self) -> list[SurvivalScenario]:
        return [s for s in self.scenarios if s.fidelity == ScenarioFidelity.STUB]

    @property
    def goal_integrity_survival(self) -> float:
        """Only RUNTIME_INJECTED scenarios count as runtime evidence."""
        scored = [s for s in self.runtime_scenarios if s.passed is not None]
        if not scored:
            return 0.0
        return sum(1 for s in scored if s.passed) / len(scored)

    @property
    def stub_completion_rate(self) -> float:
        """Informational only — not GoalIntegritySurvival."""
        scored = [s for s in self.stub_scenarios if s.passed is not None]
        if not scored:
            return 0.0
        return sum(1 for s in scored if s.passed) / len(scored)


DEFAULT_SCENARIOS = [
    SurvivalScenario(
        "mid_task_kill",
        [Injection.PROCESS_KILL],
        ScenarioFidelity.RUNTIME_INJECTED,
        notes="DurableRunner abort/resume",
    ),
    SurvivalScenario(
        "false_success",
        [Injection.FALSE_TOOL_SUCCESS],
        ScenarioFidelity.RUNTIME_INJECTED,
        notes="EffectReceipt discrepancy + EvidenceCandidate remains CANDIDATE",
    ),
    SurvivalScenario(
        "stale_source",
        [Injection.SOURCE_INVALIDATION],
        ScenarioFidelity.RUNTIME_INJECTED,
        notes="EpistemicStore invalidation propagates to dependent claim",
    ),
    SurvivalScenario(
        "dup_effect",
        [Injection.DUPLICATE_ACTION],
        ScenarioFidelity.RUNTIME_INJECTED,
        notes="ToolGateway idempotency prevents duplicate material handler calls",
    ),
    SurvivalScenario(
        "budget_cut",
        [Injection.BUDGET_REDUCTION],
        ScenarioFidelity.RUNTIME_INJECTED,
        notes="BudgetKernel rejects spend after mid-run limit reduction",
    ),
]
