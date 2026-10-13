"""Mission Learning Loop v0 — archive → diagnose → 2 candidates → tournament."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from global_os.evals.mission_learning.archive import MissionArchive
from global_os.evals.mission_learning.schemas import (
    assert_not_auto_promoted,
    validate_improvement_candidate,
    validate_mission_record,
)
from global_os.evals.mission_learning.scorer import better_than_parent, score_workflow_policy

# Frozen public training suite — never Challenge-GA.
PUBLIC_TRAIN_SUITE_ID = "mll_v0_public_tool_selection_v1"
TRANSFER_SUITE_ID = "mll_v0_transfer_holdout_NOT_RUN"


class MissionLearningError(RuntimeError):
    pass


def example_mission_record(*, parent_version: str = "fixture_parent") -> dict[str, Any]:
    """Synthetic mission with confirmed wrong_tool_selection inefficiency."""
    return {
        "record_id": "mr_fixture_wrong_tool_001",
        "schema_version": "mission_record_v0",
        "goal": {
            "goal_id": "goal_fixture_research_note",
            "objective_text": "Write a checkable research note using filesystem tools",
            "success_criteria_ids": ["sc_note"],
        },
        "initial_plan": {
            "plan_id": "plan_001",
            "tasks": [
                {"task_id": "t1", "task_type": "read_source", "title": "read"},
                {"task_id": "t2", "task_type": "write_note", "title": "write"},
            ],
        },
        "strategy_changes": [
            {
                "at_step": "t2",
                "from_approach": "web.read",
                "to_approach": "filesystem.write",
                "why": "wrong_tool_then_corrected",
            }
        ],
        "failures": [
            {
                "failure_class": "wrong_tool_selection",
                "detail": "selected web.read for write_note task",
                "confirmed": True,
            }
        ],
        "costs": {
            "tokens": 12000,
            "tool_calls": 6,
            "wall_seconds": 90,
            "usd_estimate": 0.4,
        },
        "verified_outcome": {
            "terminal": "PARTIAL",
            "verified": True,
            "evidence_refs": ["receipt_note_written"],
        },
        "provenance": {
            "parent_version": parent_version,
            "recorded_at_utc": datetime.now(UTC).isoformat(),
            "source": "synthetic_fixture",
        },
    }


def public_training_tasks() -> list[dict[str, Any]]:
    return [
        {
            "task_id": "a1",
            "task_type": "read_source",
            "correct_tool": "filesystem.read",
            "base_tokens": 10,
            "retry_tokens": 40,
        },
        {
            "task_id": "a2",
            "task_type": "write_note",
            "correct_tool": "filesystem.write",
            "base_tokens": 12,
            "retry_tokens": 45,
        },
        {
            "task_id": "a3",
            "task_type": "write_note",
            "correct_tool": "filesystem.write",
            "base_tokens": 12,
            "retry_tokens": 45,
        },
        {
            "task_id": "a4",
            "task_type": "read_source",
            "correct_tool": "filesystem.read",
            "base_tokens": 10,
            "retry_tokens": 40,
        },
    ]


def diagnose_failure_class(record: dict[str, Any]) -> str:
    for f in record.get("failures") or []:
        if f.get("confirmed") and f.get("failure_class"):
            return str(f["failure_class"])
    raise MissionLearningError("no confirmed failure_class in mission record")


def _baseline_policy() -> dict[str, Any]:
    # Intentionally weak: wrong default for write_note
    return {
        "policy_id": "baseline_parent",
        "default_tool": "web.read",
        "tool_by_task_type": {"read_source": "filesystem.read"},
    }


def _candidate_policies() -> tuple[dict[str, Any], dict[str, Any]]:
    good = {
        "policy_id": "cand_typed_tools",
        "default_tool": "filesystem.read",
        "tool_by_task_type": {
            "read_source": "filesystem.read",
            "write_note": "filesystem.write",
        },
    }
    mediocre = {
        "policy_id": "cand_always_write",
        "default_tool": "filesystem.write",
        "tool_by_task_type": {
            "read_source": "filesystem.write",
            "write_note": "filesystem.write",
        },
    }
    return good, mediocre


def _mk_candidate(
    *,
    candidate_id: str,
    parent_version: str,
    failure_class: str,
    proposed_change: str,
    policy: dict[str, Any],
    minimum_improvement: float,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "parent_version": parent_version,
        "target_component": "tool_selection_policy",
        "failure_class": failure_class,
        "proposed_change": proposed_change,
        "falsifiable_prediction": {
            "expected": "fewer_wrong_tool_calls",
            "minimum_improvement": minimum_improvement,
        },
        "evaluation": {
            "training_suite": PUBLIC_TRAIN_SUITE_ID,
            "transfer_suite": TRANSFER_SUITE_ID,
            "compare_against": "unchanged_parent",
            "budget": {"max_tokens": 50_000, "max_trials": 1},
            "independent_scorer": True,
        },
        "safety": {
            "mutation_scope": "unprivileged_harness_only",
            "authority_changes": "forbidden",
            "scorer_changes": "forbidden",
            "sandbox": "required",
            "challenge_ga_as_train": "forbidden",
        },
        "complexity": {
            "added_tokens_estimate": 200,
            "added_latency_ms_estimate": 5.0,
            "added_dependencies": [],
            "deletion_test": "pending",
        },
        "promotion": {
            "regression_free": "not_run",
            "benefit_confirmed": "not_run",
            "human_approval": "required",
            "status": "REQUIRES_HUMAN",
        },
        "result": "NOT_RUN",
        "_policy": policy,  # harness-private; stripped before archive validate
    }


def refuse_privileged_candidate(cand: dict[str, Any]) -> None:
    """Adversarial gate: Authority/scorer mutations never enter tournament."""
    text = f"{cand.get('proposed_change', '')} {cand.get('target_component', '')}".lower()
    for token in (
        "authority",
        "scorer",
        "challenge_ga",
        "execution_token",
        "holdout",
        "rollback_infra",
    ):
        if token in text:
            raise MissionLearningError(f"privileged or forbidden mutation refused: {token}")


def run_mission_learning_loop_v0(
    *,
    mission_record: dict[str, Any] | None = None,
    parent_version: str = "fixture_parent",
    archive: MissionArchive | None = None,
    minimum_improvement: float = 1.0,
) -> dict[str, Any]:
    """Run MLLv0 end-to-end. Never auto-promotes; never uses Challenge-GA train."""
    archive = archive or MissionArchive()
    record = validate_mission_record(
        mission_record or example_mission_record(parent_version=parent_version)
    )
    archive.add_mission(record)
    failure_class = diagnose_failure_class(record)
    if failure_class != "wrong_tool_selection":
        # v0 fixture loop specializes this class; other classes archive-only.
        raise MissionLearningError(
            f"v0 harness supports wrong_tool_selection only, got {failure_class}"
        )

    tasks = public_training_tasks()
    baseline_policy = _baseline_policy()
    cand_a_policy, cand_b_policy = _candidate_policies()

    baseline_score = score_workflow_policy(policy=baseline_policy, tasks=tasks)
    candidates_raw = [
        _mk_candidate(
            candidate_id="IMP-001",
            parent_version=parent_version,
            failure_class=failure_class,
            proposed_change="typed_tool_by_task_type_policy",
            policy=cand_a_policy,
            minimum_improvement=minimum_improvement,
        ),
        _mk_candidate(
            candidate_id="IMP-002",
            parent_version=parent_version,
            failure_class=failure_class,
            proposed_change="always_filesystem_write_policy",
            policy=cand_b_policy,
            minimum_improvement=minimum_improvement,
        ),
    ]
    if len(candidates_raw) != 2:
        raise MissionLearningError("v0 requires exactly two candidates")

    scored: list[dict[str, Any]] = []
    for raw in candidates_raw:
        refuse_privileged_candidate(raw)
        policy = raw.pop("_policy")
        score = score_workflow_policy(policy=policy, tasks=tasks)
        win = better_than_parent(
            candidate_score=score,
            parent_score=baseline_score,
            minimum_improvement=minimum_improvement,
        )
        # Regression-free: success_rate must not drop
        regression_free = score["success_rate"] + 1e-9 >= baseline_score["success_rate"]
        raw["score"] = score
        raw["result"] = "WIN" if win and regression_free else "LOSS"
        raw["promotion"]["regression_free"] = "passed" if regression_free else "failed"
        raw["promotion"]["benefit_confirmed"] = "passed" if win else "failed"
        # Wins still need human; losses archived as negative evidence (no promote).
        raw["promotion"]["status"] = (
            "REQUIRES_HUMAN" if raw["result"] == "WIN" else "ARCHIVED_NEGATIVE"
        )
        raw["promotion"]["human_approval"] = "required"
        if raw["result"] == "WIN" and not raw["complexity"]["added_dependencies"]:
            raw["complexity"]["deletion_test"] = "keep_helps"
        else:
            raw["complexity"]["deletion_test"] = "not_run"
        assert_not_auto_promoted(raw)
        validate_improvement_candidate(raw)
        archive.add_candidate(raw)
        scored.append(raw)

    losses = [c for c in scored if c["result"] == "LOSS"]
    wins = [c for c in scored if c["result"] == "WIN"]

    tournament = {
        "suite_id": PUBLIC_TRAIN_SUITE_ID,
        "transfer_suite_id": TRANSFER_SUITE_ID,
        "transfer_run": "NOT_RUN",
        "baseline_score": baseline_score,
        "candidates": [
            {
                "candidate_id": c["candidate_id"],
                "result": c["result"],
                "score": c.get("score"),
                "promotion_status": c["promotion"]["status"],
            }
            for c in scored
        ],
        "auto_promoted": False,
        "promotions_applied": 0,
        "human_required": True,
        "challenge_ga_used_as_train": False,
        "archived_at_utc": datetime.now(UTC).isoformat(),
    }
    archive.add_tournament_result(tournament)

    return {
        "mission_record_id": record["record_id"],
        "failure_class": failure_class,
        "baseline_score": baseline_score,
        "candidates": deepcopy(scored),
        "wins": [c["candidate_id"] for c in wins],
        "losses": [c["candidate_id"] for c in losses],
        "tournament": tournament,
        "archive_counts": {
            "missions": len(archive.records),
            "candidates": len(archive.candidates),
            "tournaments": len(archive.tournament_results),
        },
        "auto_promoted": False,
        "continual_si_claim": "NOT_MEASURED",
    }
