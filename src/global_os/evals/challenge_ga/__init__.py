"""CHALLENGE-GA-v1 eval harness — terminal scoring + organ fixture loop (T2/eval)."""

from global_os.evals.challenge_ga.exec_gate import (
    ChallengeExecForbidden,
    assert_challenge_exec_authorized,
    prepare_challenge_exec,
)
from global_os.evals.challenge_ga.fixture_loop import (
    build_challenge_goal,
    run_organ_fixture_loop,
)
from global_os.evals.challenge_ga.scorer import score_terminal_fixture

__all__ = [
    "ChallengeExecForbidden",
    "assert_challenge_exec_authorized",
    "build_challenge_goal",
    "prepare_challenge_exec",
    "run_organ_fixture_loop",
    "score_terminal_fixture",
]
