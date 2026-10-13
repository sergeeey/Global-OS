"""Schema validation for Mission Learning Loop v0 (no regex-as-contract)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
PACK = ROOT / "artifacts" / "pilot" / "mission_learning"

# Challenge-GA and sealed exams must never be training suites for MLLv0.
FORBIDDEN_TRAIN_SUITES: frozenset[str] = frozenset(
    {
        "challenge_ga",
        "CHALLENGE-GA-v1",
        "artifacts/pilot/challenge_ga",
        "challenge_ga/target_fixture",
    }
)

_PRIVILEGED_SCOPES: frozenset[str] = frozenset(
    {
        "authority",
        "scorer",
        "holdout",
        "rollback_infra",
        "t0",
        "t1_kernel",
    }
)


def _load_schema(name: str) -> dict[str, Any]:
    path = PACK / name
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"{name} must be object")
    return raw


def _require_keys(obj: dict[str, Any], keys: tuple[str, ...], *, label: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ValueError(f"{label} missing keys: {missing}")


def validate_mission_record(record: dict[str, Any]) -> dict[str, Any]:
    """Structural validate MissionRecord (schema file is source of required keys)."""
    schema = _load_schema("MISSION_RECORD.schema.json")
    required = tuple(schema.get("required") or [])
    _require_keys(record, required, label="mission_record")
    if record.get("schema_version") != "mission_record_v0":
        raise ValueError("mission_record schema_version must be mission_record_v0")
    goal = record["goal"]
    if not isinstance(goal, dict) or not goal.get("goal_id") or not goal.get("objective_text"):
        raise ValueError("mission_record.goal incomplete")
    costs = record["costs"]
    if not isinstance(costs, dict):
        raise TypeError("costs must be object")
    for k in ("tokens", "tool_calls", "wall_seconds"):
        if k not in costs:
            raise ValueError(f"costs missing {k}")
    outcome = record["verified_outcome"]
    if not isinstance(outcome, dict) or "verified" not in outcome:
        raise ValueError("verified_outcome incomplete")
    return record


def validate_improvement_candidate(cand: dict[str, Any]) -> dict[str, Any]:
    schema = _load_schema("IMPROVEMENT_CANDIDATE.schema.json")
    required = tuple(schema.get("required") or [])
    _require_keys(cand, required, label="improvement_candidate")
    safety = cand["safety"]
    if safety.get("mutation_scope") != "unprivileged_harness_only":
        raise ValueError("only unprivileged_harness_only mutations allowed")
    if safety.get("authority_changes") != "forbidden":
        raise ValueError("authority_changes must be forbidden")
    if safety.get("scorer_changes") != "forbidden":
        raise ValueError("scorer_changes must be forbidden")
    if safety.get("sandbox") != "required":
        raise ValueError("sandbox must be required")
    if safety.get("challenge_ga_as_train") != "forbidden":
        raise ValueError("challenge_ga_as_train must be forbidden")
    evaluation = cand["evaluation"]
    train = str(evaluation.get("training_suite") or "")
    if train in FORBIDDEN_TRAIN_SUITES or "challenge_ga" in train.lower():
        raise ValueError("Challenge-GA must not be used as training suite")
    if evaluation.get("independent_scorer") is not True:
        raise ValueError("independent_scorer required")
    if evaluation.get("compare_against") != "unchanged_parent":
        raise ValueError("compare_against must be unchanged_parent")
    promotion = cand["promotion"]
    if promotion.get("human_approval") != "required":
        raise ValueError("human_approval must be required")
    if promotion.get("status") == "PROMOTED_BY_HUMAN":
        # Harness never sets this; only explicit human path may.
        raise ValueError("harness must not self-set PROMOTED_BY_HUMAN")
    complexity = cand["complexity"]
    for k in (
        "added_tokens_estimate",
        "added_latency_ms_estimate",
        "added_dependencies",
        "deletion_test",
    ):
        if k not in complexity:
            raise ValueError(f"complexity missing {k}")
    scope = str(cand.get("proposed_change") or "").lower()
    for bad in _PRIVILEGED_SCOPES:
        if bad in scope and cand.get("target_component") not in {
            "orchestration",
            "decomposer",
            "pivot_replan",
            "workflow_unprivileged",
            "memory_handoff",
            "tool_selection_policy",
        }:
            raise ValueError(f"privileged scope refused: {bad}")
    return cand


def assert_not_auto_promoted(cand: dict[str, Any]) -> None:
    status = (cand.get("promotion") or {}).get("status")
    if status not in {"REQUIRES_HUMAN", "REJECTED", "ARCHIVED_NEGATIVE"}:
        raise ValueError(f"illegal promotion status for harness: {status!r}")
