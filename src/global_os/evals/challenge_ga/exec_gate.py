"""Challenge-GA execution gate — fail-closed until human authorizes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from global_os.evals.challenge_ga.scorer import score_terminal_fixture

ROOT = Path(__file__).resolve().parents[4]
LOCK_PATH = ROOT / "artifacts" / "pilot" / "challenge_ga" / "LOCK.json"

# Explicit human-request tokens (never inferred from env alone for AUTHORIZED)
HUMAN_REQUEST_TOKENS = frozenset(
    {
        "HUMAN_REQUEST_CHALLENGE_GA_EXEC",
    }
)


class ChallengeExecForbidden(RuntimeError):
    """Raised when Challenge execution is attempted without authorization."""


def load_challenge_lock(path: Path | None = None) -> dict[str, Any]:
    raw = json.loads((path or LOCK_PATH).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("CHALLENGE-GA LOCK.json must be an object")
    return raw


def assert_challenge_exec_authorized(
    *,
    human_request_token: str | None = None,
    lock: dict[str, Any] | None = None,
    lock_path: Path | None = None,
) -> dict[str, Any]:
    """Allow exec only if lock says AUTHORIZED or explicit human token is presented.

    Lock default is NOT_STARTED — runners must call this before any arm loop that
    mutates the world / scores Challenge WIN.
    """
    data = lock if lock is not None else load_challenge_lock(lock_path)
    status = str(data.get("execution_status") or "NOT_STARTED")
    if status == "AUTHORIZED":
        return data
    if human_request_token in HUMAN_REQUEST_TOKENS:
        return data
    raise ChallengeExecForbidden(
        f"CHALLENGE-GA exec forbidden: execution_status={status!r}; "
        "human must set AUTHORIZED or pass HUMAN_REQUEST_CHALLENGE_GA_EXEC "
        "(forbidden: execute_before_human_request)"
    )


def prepare_challenge_exec(
    *,
    human_request_token: str | None = None,
    lock: dict[str, Any] | None = None,
    lock_path: Path | None = None,
) -> dict[str, Any]:
    """Gate + terminal scorer readiness check. Does not run arms or claim WIN.

    Returns lock + sealed terminal criteria snapshot only after authorization.
    Organ fixture loops may run without this; world-mutating Challenge exec must not.
    """
    data = assert_challenge_exec_authorized(
        human_request_token=human_request_token,
        lock=lock,
        lock_path=lock_path,
    )
    terminal = data.get("terminal_success") or {}
    # Scorer must be loadable against sealed fixture before any arm work.
    probe = score_terminal_fixture(
        sealed_checksum=int(terminal.get("sealed_checksum") or 7674672),
        ops_budget_max=int(terminal.get("ops_budget_max") or 80000),
    )
    return {
        "authorized": True,
        "lock": data,
        "scorer_ready": True,
        "naive_fixture_win": bool(probe.get("win")),
        "terminal_probe": {
            "checksum": probe.get("checksum"),
            "ops": probe.get("ops"),
            "ops_budget_max": probe.get("ops_budget_max"),
            "reason": probe.get("reason"),
        },
        "world_exec_started": False,
        "challenge_win_claimed": False,
    }
