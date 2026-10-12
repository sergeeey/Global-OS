"""AI Scientist–shaped MissionContract templates (ADR-0013).

Stages: idea → lit → code → run → figure → write.
Hard gates: prereg, mechanical tests, independent verification diversity.
LLM peer-review is advisory only — never VERIFIED (GOS-I10 / GOS-I24).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class StageId(str, Enum):
    IDEA = "idea"
    LIT = "lit"
    CODE = "code"
    RUN = "run"
    FIGURE = "figure"
    WRITE = "write"


class StageStatus(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"


@dataclass
class StageResult:
    stage: StageId
    status: StageStatus
    evidence: dict[str, Any]
    advisory_llm_review: str | None = None  # never sufficient for VERIFIED


RESEARCH_FACTORY_STAGES: tuple[StageId, ...] = (
    StageId.IDEA,
    StageId.LIT,
    StageId.CODE,
    StageId.RUN,
    StageId.FIGURE,
    StageId.WRITE,
)


def mission_contract_template(*, goal_id: str, title: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "mission_id": f"research-factory:{goal_id}",
        "goal_id": goal_id,
        "title": title,
        "template": "research_factory_v1",
        "stages": [s.value for s in RESEARCH_FACTORY_STAGES],
        "hard_gates": [
            "prereg_locked_before_run",
            "mechanical_tests_required",
            "independent_verification_diversity",
            "reject_allowed_terminal",
        ],
        "forbidden": [
            "llm_peer_review_as_verified",
            "same_model_self_certification",
            "silent_secondary_to_primary",
        ],
        "trust_zone": "T2",
    }


class ResearchFactoryRunner:
    """Deterministic stage runner for tests — REJECT is a valid terminal."""

    def __init__(self) -> None:
        self._results: list[StageResult] = []

    def run_stage(
        self,
        stage: StageId,
        *,
        prereg_locked: bool,
        mechanical_ok: bool,
        independent_diversity: bool,
        advisory_llm_review: str | None = None,
        force_reject: bool = False,
    ) -> StageResult:
        if force_reject:
            result = StageResult(
                stage, StageStatus.REJECTED, {"reason": "forced_reject"}, advisory_llm_review
            )
            self._results.append(result)
            return result

        if stage in {StageId.RUN, StageId.WRITE} and not prereg_locked:
            result = StageResult(
                stage, StageStatus.REJECTED, {"reason": "prereg_not_locked"}, advisory_llm_review
            )
            self._results.append(result)
            return result
        if stage is StageId.RUN and not mechanical_ok:
            result = StageResult(
                stage,
                StageStatus.REJECTED,
                {"reason": "mechanical_tests_failed"},
                advisory_llm_review,
            )
            self._results.append(result)
            return result
        if stage is StageId.WRITE and not independent_diversity:
            result = StageResult(
                stage,
                StageStatus.REJECTED,
                {"reason": "verification_diversity_missing"},
                advisory_llm_review,
            )
            self._results.append(result)
            return result

        # Advisory LLM review recorded but never promotes status alone.
        result = StageResult(
            stage,
            StageStatus.PASSED,
            {
                "mechanical_ok": mechanical_ok,
                "llm_review_is_advisory_only": True,
                "advisory_present": advisory_llm_review is not None,
            },
            advisory_llm_review,
        )
        self._results.append(result)
        return result

    def terminal(self) -> dict[str, Any]:
        if any(r.status is StageStatus.REJECTED for r in self._results):
            return {
                "terminal": "REJECTED",
                "stages": [r.stage.value for r in self._results if r.status is StageStatus.REJECTED],
            }
        if {r.stage for r in self._results if r.status is StageStatus.PASSED} >= set(
            RESEARCH_FACTORY_STAGES
        ):
            return {"terminal": "COMPLETED", "stages": [s.value for s in RESEARCH_FACTORY_STAGES]}
        return {"terminal": "IN_PROGRESS", "passed": [r.stage.value for r in self._results]}

    @staticmethod
    def self_cert_path_denied() -> bool:
        """Same-model self-certification path is always DENY."""
        return True
