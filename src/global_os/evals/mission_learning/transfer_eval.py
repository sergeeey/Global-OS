"""Protected transfer evaluation — benchmark-disjoint skill comparison.

Baseline vs candidate under identical budget; Challenge-GA holdout never used as train.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class TransferTrialResult:
    suite_id: str
    baseline_success_rate: float
    candidate_success_rate: float
    n_tasks: int
    budget_equal: bool
    disjoint_from_train: bool
    used_challenge_holdout: bool
    candidate_advantage: float
    promote_allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "baseline_success_rate": self.baseline_success_rate,
            "candidate_success_rate": self.candidate_success_rate,
            "n_tasks": self.n_tasks,
            "budget_equal": self.budget_equal,
            "disjoint_from_train": self.disjoint_from_train,
            "used_challenge_holdout": self.used_challenge_holdout,
            "candidate_advantage": self.candidate_advantage,
            "promote_allowed": self.promote_allowed,
            "reason": self.reason,
        }


TaskRunner = Callable[[str, dict[str, Any]], bool]


def run_transfer_trial(
    *,
    suite_id: str,
    task_ids: list[str],
    baseline_runner: TaskRunner,
    candidate_runner: TaskRunner,
    budget: dict[str, Any],
    train_task_ids: set[str] | None = None,
    is_challenge_holdout: bool = False,
) -> TransferTrialResult:
    train = train_task_ids or set()
    overlap = set(task_ids) & train
    disjoint = len(overlap) == 0
    # Challenge holdout must never be training suite; transfer trial on holdout
    # is allowed only as protected eval (is_challenge_holdout=True marks that).
    if is_challenge_holdout and not disjoint:
        return TransferTrialResult(
            suite_id=suite_id,
            baseline_success_rate=0.0,
            candidate_success_rate=0.0,
            n_tasks=len(task_ids),
            budget_equal=True,
            disjoint_from_train=False,
            used_challenge_holdout=True,
            candidate_advantage=0.0,
            promote_allowed=False,
            reason="challenge_holdout_overlap_with_train_forbidden",
        )

    base_ok = 0
    cand_ok = 0
    for tid in task_ids:
        if baseline_runner(tid, budget):
            base_ok += 1
        if candidate_runner(tid, budget):
            cand_ok += 1
    n = len(task_ids) or 1
    b_rate = base_ok / n
    c_rate = cand_ok / n
    adv = c_rate - b_rate
    # No auto-promote; require disjoint + advantage + adequate n
    promote = (
        disjoint
        and not (is_challenge_holdout and suite_id.startswith("challenge_ga"))
        and adv > 0.0
        and n >= 5
    )
    reason = "candidate_advantage" if adv > 0 else "no_advantage"
    if not disjoint:
        reason = "not_disjoint_from_train"
        promote = False
    if n < 5:
        reason = "sample_too_small_for_admission"
        promote = False
    return TransferTrialResult(
        suite_id=suite_id,
        baseline_success_rate=b_rate,
        candidate_success_rate=c_rate,
        n_tasks=len(task_ids),
        budget_equal=True,
        disjoint_from_train=disjoint,
        used_challenge_holdout=is_challenge_holdout,
        candidate_advantage=adv,
        promote_allowed=promote,
        reason=reason,
    )
