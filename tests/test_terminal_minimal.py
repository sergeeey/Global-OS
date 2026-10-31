"""Minimal terminal-integrity port for the origin preprod runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.runtime.preprod import deliver_mission, start_mission, status_mission

ROOT = Path(__file__).resolve().parents[1]


def _goal(goal_id: str) -> dict:
    goal = json.loads((ROOT / "examples" / "goal_repo_audit.json").read_text(encoding="utf-8"))
    goal["goal_id"] = goal_id
    return goal


def _run(tmp_path: Path, goal_id: str, **kwargs) -> dict:
    return start_mission(
        _goal(goal_id),
        target_path=ROOT,
        gos_root=tmp_path / ".gos",
        budget_usd=5.0,
        budget_tokens=1000,
        **kwargs,
    )


def _run_dir(tmp_path: Path, run_id: str) -> Path:
    return tmp_path / ".gos" / "missions" / run_id


def _state(tmp_path: Path, run_id: str) -> dict:
    return json.loads((_run_dir(tmp_path, run_id) / "state.json").read_text(encoding="utf-8"))


def _write_state(tmp_path: Path, run_id: str, state: dict) -> None:
    (_run_dir(tmp_path, run_id) / "state.json").write_text(
        json.dumps(state), encoding="utf-8"
    )


def _both(tmp_path: Path, run_id: str) -> tuple[dict, dict]:
    return (
        status_mission(gos_root=tmp_path / ".gos", run_id=run_id),
        deliver_mission(gos_root=tmp_path / ".gos", run_id=run_id),
    )


def test_valid_succeeded_remains_succeeded(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_success")
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "SUCCEEDED"
    assert st["control_status"] == "SUCCEEDED"
    assert st["accepted"] is True
    assert dl["accepted"] is True


def test_valid_failed_remains_failed(tmp_path: Path) -> None:
    delivery = _run(
        tmp_path,
        "goal_minimal_failed",
        hooks={"inject_tool_failure": True},
    )
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "FAILED"
    assert st["accepted"] is True


def test_normal_paused_without_delivery_remains_paused(tmp_path: Path) -> None:
    paused = _run(tmp_path, "goal_minimal_paused", kill_after_step="gateway_observe")
    assert paused["status"] == "PAUSED"
    st = status_mission(gos_root=tmp_path / ".gos", run_id=paused["run_id"])
    assert st["status"] == "PAUSED"
    assert st["control_status"] == "PAUSED"
    with pytest.raises(Exception, match="delivery not ready"):
        deliver_mission(gos_root=tmp_path / ".gos", run_id=paused["run_id"])


def test_missing_delivery_after_success_is_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_missing")
    (_run_dir(tmp_path, delivery["run_id"]) / "delivery.json").unlink()
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert st["control_status"] == "SUCCEEDED"
    assert st["accepted"] is False
    assert dl["accepted"] is False
    assert "delivery_missing" in dl["delivery_integrity"]["reasons"]


def test_delivery_control_mismatch_is_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_mismatch")
    path = _run_dir(tmp_path, delivery["run_id"]) / "delivery.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["terminal_status"] = "FAILED"
    path.write_text(json.dumps(raw), encoding="utf-8")
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert dl["accepted"] is False
    assert "control_delivery_mismatch" in dl["delivery_integrity"]["reasons"]


def test_missing_artifact_is_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_artifact_missing")
    state = _state(tmp_path, delivery["run_id"])
    digest = str(state["artifact_digest"]).split(":", 1)[1]
    (_run_dir(tmp_path, delivery["run_id"]) / "artifacts" / "sha256" / digest).unlink()
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert "artifact_missing" in dl["delivery_integrity"]["reasons"]


def test_tampered_artifact_is_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_artifact_tampered")
    state = _state(tmp_path, delivery["run_id"])
    digest = str(state["artifact_digest"]).split(":", 1)[1]
    artifact = _run_dir(tmp_path, delivery["run_id"]) / "artifacts" / "sha256" / digest
    artifact.write_bytes(b"tampered")
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert "artifact_digest_mismatch" in dl["delivery_integrity"]["reasons"]


def test_empty_receipts_are_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_empty_receipts")
    state = _state(tmp_path, delivery["run_id"])
    state["effect_receipts"] = []
    _write_state(tmp_path, delivery["run_id"], state)
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert "no_effect_receipts" in dl["delivery_integrity"]["reasons"]


def test_failed_artifact_verify_is_inconclusive(tmp_path: Path) -> None:
    delivery = _run(tmp_path, "goal_minimal_verify_false")
    state = _state(tmp_path, delivery["run_id"])
    state["artifact_verify"] = {"ok": False, "reason": "tampered"}
    _write_state(tmp_path, delivery["run_id"], state)
    st, dl = _both(tmp_path, delivery["run_id"])
    assert st["status"] == dl["terminal_status"] == "INCONCLUSIVE"
    assert "artifact_verify_failed" in dl["delivery_integrity"]["reasons"]
