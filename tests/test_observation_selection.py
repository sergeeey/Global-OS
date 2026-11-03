"""Observation-selection experiment: missing / empty / non-empty targets."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.runtime.preprod import deliver_mission, start_mission, status_mission

ROOT = Path(__file__).resolve().parents[1]
GOAL = json.loads((ROOT / "examples" / "goal_repo_audit.json").read_text(encoding="utf-8"))


def _run(tmp_path: Path, goal_id: str, target: Path) -> dict:
    return start_mission(
        {**GOAL, "goal_id": goal_id},
        target_path=target,
        gos_root=tmp_path / ".gos",
        budget_usd=5.0,
        budget_tokens=1000,
    )


def _state(tmp_path: Path, run_id: str) -> dict:
    return json.loads(
        (tmp_path / ".gos" / "missions" / run_id / "state.json").read_text(
            encoding="utf-8"
        )
    )


def test_missing_target_is_rejected_by_observation(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_obs_missing", tmp_path / "missing")
    state = _state(tmp_path, delivery["run_id"])
    assert delivery["terminal_status"] == "INCONCLUSIVE"
    assert state["observe_block"] == "invalid_target"
    assert not delivery["completion"]["criteria_met"]


def test_empty_target_is_audit_not_applicable(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()
    delivery = _run(tmp_path, "goal_obs_empty", target)
    state = _state(tmp_path, delivery["run_id"])
    assert delivery["terminal_status"] == "INCONCLUSIVE"
    assert state["observe_block"] == "audit_not_applicable"
    assert state["observation"]["file_count"] == 0
    assert not delivery["completion"]["criteria_met"]


def test_non_empty_target_runs_inventory_then_audit(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    target.mkdir()
    (target / "README.md").write_text("# repo\n", encoding="utf-8")
    (target / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    delivery = _run(tmp_path, "goal_obs_nonempty", target)
    state = _state(tmp_path, delivery["run_id"])
    assert delivery["terminal_status"] == "SUCCEEDED"
    assert delivery["observation"]["tool_id"] == "repo.inventory"
    assert state["observation"]["file_count"] == 2
    assert delivery["tool_calls"] == {"repo.audit": 1}
    assert delivery["completion"]["status"] == "ACHIEVED"


def test_selector_effective_terminal_matches_status(tmp_path: Path) -> None:
    target = tmp_path / "empty"
    target.mkdir()
    delivery = _run(tmp_path, "goal_obs_semantics", target)
    st = status_mission(gos_root=tmp_path / ".gos", run_id=delivery["run_id"])
    dl = deliver_mission(gos_root=tmp_path / ".gos", run_id=delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert st["accepted"] == dl["accepted"]
