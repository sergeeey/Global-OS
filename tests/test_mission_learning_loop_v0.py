"""Mission Learning Loop v0 — acceptance + adversarial gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.mission_learning import (
    FORBIDDEN_TRAIN_SUITES,
    MissionArchive,
    MissionLearningError,
    run_mission_learning_loop_v0,
    validate_improvement_candidate,
    validate_mission_record,
)
from global_os.evals.mission_learning.loop import (
    PUBLIC_TRAIN_SUITE_ID,
    example_mission_record,
    refuse_privileged_candidate,
)
from global_os.evals.mission_learning.schemas import assert_not_auto_promoted

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "artifacts" / "pilot" / "mission_learning"


def test_pack_and_adr_exist() -> None:
    assert (PACK / "MISSION_LEARNING_LOOP_V0.md").is_file()
    assert (PACK / "MISSION_RECORD.schema.json").is_file()
    assert (PACK / "IMPROVEMENT_CANDIDATE.schema.json").is_file()
    assert (PACK / "P1_ACHIEVER_GATE.md").is_file()
    assert (ROOT / "docs" / "adr" / "ADR-0014-goal-conditioned-continual-improvement.md").is_file()


def test_loop_archives_mission_two_candidates_baseline_no_autopromote() -> None:
    archive = MissionArchive()
    out = run_mission_learning_loop_v0(archive=archive)
    assert out["auto_promoted"] is False
    assert out["continual_si_claim"] == "NOT_MEASURED"
    assert out["failure_class"] == "wrong_tool_selection"
    assert len(out["candidates"]) == 2
    assert out["archive_counts"]["missions"] == 1
    assert out["archive_counts"]["candidates"] == 2
    assert out["tournament"]["challenge_ga_used_as_train"] is False
    assert out["tournament"]["suite_id"] == PUBLIC_TRAIN_SUITE_ID
    assert "IMP-001" in out["wins"]
    assert out["losses"]  # mediocre candidate should lose
    for c in out["candidates"]:
        assert c["promotion"]["human_approval"] == "required"
        assert c["promotion"]["status"] in {"REQUIRES_HUMAN", "ARCHIVED_NEGATIVE"}
        assert "deletion_test" in c["complexity"]
        assert_not_auto_promoted(c)


def test_challenge_ga_forbidden_as_train_suite() -> None:
    cand = {
        "candidate_id": "IMP-X",
        "parent_version": "p",
        "target_component": "orchestration",
        "failure_class": "x",
        "proposed_change": "y",
        "falsifiable_prediction": {"expected": "e", "minimum_improvement": 1},
        "evaluation": {
            "training_suite": "challenge_ga",
            "transfer_suite": "t",
            "compare_against": "unchanged_parent",
            "budget": {"max_tokens": 1, "max_trials": 1},
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
            "added_tokens_estimate": 0,
            "added_latency_ms_estimate": 0,
            "added_dependencies": [],
            "deletion_test": "pending",
        },
        "promotion": {
            "regression_free": "required",
            "benefit_confirmed": "required",
            "human_approval": "required",
            "status": "REQUIRES_HUMAN",
        },
        "result": "NOT_RUN",
    }
    with pytest.raises(ValueError, match="Challenge-GA"):
        validate_improvement_candidate(cand)
    assert "challenge_ga" in FORBIDDEN_TRAIN_SUITES or any(
        "challenge" in s.lower() for s in FORBIDDEN_TRAIN_SUITES
    )


def test_refuse_authority_and_scorer_mutations() -> None:
    with pytest.raises(MissionLearningError, match="privileged"):
        refuse_privileged_candidate(
            {
                "proposed_change": "weaken authority default deny",
                "target_component": "tool_selection_policy",
            }
        )
    with pytest.raises(MissionLearningError, match="privileged"):
        refuse_privileged_candidate(
            {"proposed_change": "edit independent scorer thresholds", "target_component": "x"}
        )


def test_harness_cannot_self_set_promoted() -> None:
    cand = {
        "candidate_id": "IMP-Y",
        "parent_version": "p",
        "target_component": "workflow_unprivileged",
        "failure_class": "x",
        "proposed_change": "z",
        "falsifiable_prediction": {"expected": "e", "minimum_improvement": 0},
        "evaluation": {
            "training_suite": PUBLIC_TRAIN_SUITE_ID,
            "transfer_suite": "t",
            "compare_against": "unchanged_parent",
            "budget": {"max_tokens": 1, "max_trials": 1},
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
            "added_tokens_estimate": 0,
            "added_latency_ms_estimate": 0,
            "added_dependencies": [],
            "deletion_test": "pending",
        },
        "promotion": {
            "regression_free": "passed",
            "benefit_confirmed": "passed",
            "human_approval": "required",
            "status": "PROMOTED_BY_HUMAN",
        },
        "result": "WIN",
    }
    with pytest.raises(ValueError, match="PROMOTED_BY_HUMAN"):
        validate_improvement_candidate(cand)


def test_archive_refuses_auto_promoted_flag(tmp_path: Path) -> None:
    arch = MissionArchive()
    with pytest.raises(ValueError, match="auto_promoted"):
        arch.add_tournament_result({"auto_promoted": True})
    out = run_mission_learning_loop_v0(archive=arch)
    arch.persist(tmp_path)
    assert (tmp_path / "missions.json").is_file()
    missions = json.loads((tmp_path / "missions.json").read_text(encoding="utf-8"))
    assert missions[0]["record_id"] == out["mission_record_id"]


def test_mission_record_schema_roundtrip() -> None:
    rec = example_mission_record()
    validate_mission_record(rec)
    schema = json.loads((PACK / "MISSION_RECORD.schema.json").read_text(encoding="utf-8"))
    for key in schema["required"]:
        assert key in rec


def test_challenge_lock_still_not_started() -> None:
    lock = json.loads(
        (ROOT / "artifacts" / "pilot" / "challenge_ga" / "LOCK.json").read_text(
            encoding="utf-8"
        )
    )
    assert lock["execution_status"] == "NOT_STARTED"
