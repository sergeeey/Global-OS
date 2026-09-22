"""Tests for provider IV replay — never fabricates live success without keys."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.research.provider_iv_replay import mission_payload, replay_mission


def test_replay_blocked_without_keys(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    root = tmp_path / "Y17-fake"
    root.mkdir()
    (root / "claims.json").write_text(
        json.dumps({"decision": "SUPPORTED", "statement": "toy claim"}),
        encoding="utf-8",
    )
    (root / "preregistration.json").write_text(
        json.dumps({"primary_criterion": {"alpha": 0.05}}),
        encoding="utf-8",
    )
    (root / "verification.json").write_text(
        json.dumps({"provider_status": "BLOCKED_ENVIRONMENT"}),
        encoding="utf-8",
    )
    (root / "mission.json").write_text(
        json.dumps({"mission_id": "Y17-fake", "decision": "SUPPORTED"}),
        encoding="utf-8",
    )
    (root / "experiments" / "metrics").mkdir(parents=True)
    (root / "experiments" / "metrics" / "run.json").write_text(
        json.dumps({"decision": "SUPPORTED"}),
        encoding="utf-8",
    )
    (root / "decision.md").write_text("# Decision\n\n**SUPPORTED**\n", encoding="utf-8")

    delta = replay_mission(root)
    assert delta["after"]["status"] == "BLOCKED_ENVIRONMENT"
    assert delta["delta"]["still_blocked"] is True
    assert delta["delta"]["unblocked"] is False
    assert (root / "verification_delta.json").exists()


def test_mission_payload_from_y17_1_artifacts():
    root = Path("/workspace/artifacts/y17/Y17-1-HB2-1n-confirmatory")
    if not root.exists():
        return
    payload = mission_payload(root)
    assert "SUPPORTED" in payload["claim"] or "REJECTED" in payload["claim"]
    assert payload["before_provider_status"] in {
        "BLOCKED_ENVIRONMENT",
        "AVAILABLE",
        "NOT_REQUESTED",
        "UNKNOWN",
    }
