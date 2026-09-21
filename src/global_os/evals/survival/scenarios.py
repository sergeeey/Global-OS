"""Survival Benchmark scaffold — GoalIntegritySurvival injections."""

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


@dataclass
class SurvivalScenario:
    name: str
    injections: list[Injection]
    duration_hours: float = 24.0
    passed: bool | None = None
    notes: str = ""


@dataclass
class SurvivalReport:
    scenarios: list[SurvivalScenario] = field(default_factory=list)

    @property
    def goal_integrity_survival(self) -> float:
        scored = [s for s in self.scenarios if s.passed is not None]
        if not scored:
            return 0.0
        return sum(1 for s in scored if s.passed) / len(scored)


DEFAULT_SCENARIOS = [
    SurvivalScenario("mid_task_kill", [Injection.PROCESS_KILL]),
    SurvivalScenario("false_success", [Injection.FALSE_TOOL_SUCCESS]),
    SurvivalScenario("stale_source", [Injection.SOURCE_INVALIDATION]),
    SurvivalScenario("dup_effect", [Injection.DUPLICATE_ACTION]),
    SurvivalScenario("budget_cut", [Injection.BUDGET_REDUCTION]),
]
