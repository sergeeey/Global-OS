"""Skill Transfer Trial — post-Challenge prep (exec gated).

Baseline vs candidate on disjoint tasks. Does not run Challenge-GA.
Continual SI remains NOT_MEASURED until a human-authorized Challenge
completes and a transfer trial is scored.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from global_os.evals.challenge_ga.exec_gate import load_challenge_lock
from global_os.evals.mission_learning.transfer_eval import (
    TransferTrialResult,
    run_transfer_trial,
)


class SkillTransferForbidden(Exception):
    """Raised when transfer trial would run before Challenge readiness."""


@dataclass(frozen=True)
class SkillTransferPrep:
    status: str
    challenge_execution_status: str
    continual_si: str
    transfer_allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "challenge_execution_status": self.challenge_execution_status,
            "continual_si": self.continual_si,
            "transfer_allowed": self.transfer_allowed,
            "reason": self.reason,
            "auto_promote": False,
            "challenge_ga_as_train": "forbidden",
        }


def prepare_skill_transfer_trial(
    *,
    require_challenge_completed: bool = True,
) -> SkillTransferPrep:
    """Fail-closed prep. Default: Challenge must be COMPLETED (not just authorized)."""
    lock = load_challenge_lock()
    exec_status = str(lock.get("execution_status") or "NOT_STARTED")
    if require_challenge_completed and exec_status != "COMPLETED":
        return SkillTransferPrep(
            status="PREP_BLOCKED",
            challenge_execution_status=exec_status,
            continual_si="NOT_MEASURED",
            transfer_allowed=False,
            reason="challenge_not_completed",
        )
    return SkillTransferPrep(
        status="PREP_READY",
        challenge_execution_status=exec_status,
        continual_si="NOT_MEASURED",
        transfer_allowed=True,
        reason="challenge_completed_transfer_may_run",
    )


def run_skill_transfer_trial_gated(
    *,
    suite_id: str,
    task_ids: list[str],
    baseline_runner: Any,
    candidate_runner: Any,
    budget: dict[str, Any],
    train_task_ids: set[str] | None = None,
    force_prep_override: bool = False,
) -> TransferTrialResult:
    """Run protected transfer only when Challenge COMPLETED (or explicit test override)."""
    prep = prepare_skill_transfer_trial(
        require_challenge_completed=not force_prep_override
    )
    if not prep.transfer_allowed and not force_prep_override:
        raise SkillTransferForbidden(
            f"skill transfer forbidden: {prep.reason} "
            f"(challenge={prep.challenge_execution_status})"
        )
    result = run_transfer_trial(
        suite_id=suite_id,
        task_ids=task_ids,
        baseline_runner=baseline_runner,
        candidate_runner=candidate_runner,
        budget=budget,
        train_task_ids=train_task_ids,
        is_challenge_holdout=False,
    )
    # Never mark Continual SI measured from a forced override path
    if force_prep_override:
        # promote_allowed may be True from rates; trial still not Continual SI claim
        return TransferTrialResult(
            suite_id=result.suite_id,
            baseline_success_rate=result.baseline_success_rate,
            candidate_success_rate=result.candidate_success_rate,
            n_tasks=result.n_tasks,
            budget_equal=result.budget_equal,
            disjoint_from_train=result.disjoint_from_train,
            used_challenge_holdout=result.used_challenge_holdout,
            candidate_advantage=result.candidate_advantage,
            promote_allowed=False,
            reason=f"{result.reason};continual_si_not_measured_forced_override",
        )
    return result
