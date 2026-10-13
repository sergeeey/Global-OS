"""Challenge-GA organ loop, terminal scorer, exec gate."""

from __future__ import annotations

import pytest

from global_os.evals.challenge_ga import (
    ChallengeExecForbidden,
    assert_challenge_exec_authorized,
    build_challenge_goal,
    prepare_challenge_exec,
    run_organ_fixture_loop,
    score_terminal_fixture,
)
from global_os.evals.challenge_ga.exec_gate import load_challenge_lock


def test_terminal_scorer_naive_fixture_is_not_win():
    score = score_terminal_fixture()
    assert score["checksum"] == 7674672
    assert score["ops"] == 160000
    assert score["ops"] > score["ops_budget_max"]
    assert score["win"] is False
    assert score["reason"] == "terminal_criteria_unmet"


def test_organ_fixture_loop_decomposes_routes_pivots_without_win_claim():
    out = run_organ_fixture_loop(attempt_budget=2, simulate_failure=True)
    assert out["challenge_win_claimed"] is False
    assert out["world_effects"] is False
    assert out["route"]["decision"] == "ROUTE"
    assert out["route"]["selection"]["on_failure"] == "pivot_handoff"
    assert out["pivot"] is not None
    assert out["pivot"]["decision"] == "PIVOT"
    assert out["pivot"]["selection"]["why_failed"] == "ops_above_budget"
    assert out["terminal_score"]["win"] is False
    assert out["stop"] == "PIVOTED_AWAITING_EXEC"
    assert out["task_advances_criteria"]
    assert out["completion_gate"]["status"] != "ACHIEVED"
    assert "sc_ops" in out["completion_gate"]["criteria_unmet"]


def test_build_challenge_goal_binds_terminal_criteria():
    goal = build_challenge_goal()
    ids = {c["id"] for c in goal["success_criteria"]}
    assert ids == {"sc_checksum", "sc_ops", "sc_api"}
    assert goal["content_hash"]


def test_exec_gate_blocks_without_human():
    lock = load_challenge_lock()
    assert lock["execution_status"] == "NOT_STARTED"
    with pytest.raises(ChallengeExecForbidden, match="forbidden"):
        assert_challenge_exec_authorized()


def test_exec_gate_allows_explicit_human_token():
    data = assert_challenge_exec_authorized(
        human_request_token="HUMAN_REQUEST_CHALLENGE_GA_EXEC"
    )
    assert data["protocol_id"] == "CHALLENGE-GA-v1"


def test_prepare_challenge_exec_requires_human_and_scorer_ready():
    with pytest.raises(ChallengeExecForbidden):
        prepare_challenge_exec()
    ready = prepare_challenge_exec(
        human_request_token="HUMAN_REQUEST_CHALLENGE_GA_EXEC"
    )
    assert ready["authorized"] is True
    assert ready["scorer_ready"] is True
    assert ready["world_exec_started"] is False
    assert ready["challenge_win_claimed"] is False
    # Naive sealed fixture is not a WIN — arms must still optimize.
    assert ready["naive_fixture_win"] is False
    assert ready["terminal_probe"]["checksum"] == 7674672
