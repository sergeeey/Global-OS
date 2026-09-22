"""Artifact-first handoff — regression for recurring information_loss fix."""

from __future__ import annotations

from pathlib import Path

from global_os.evals.organization.artifact_handoff import (
    information_loss_from_envelopes,
    read_stage_artifact,
    write_stage_artifact,
)


def test_artifact_handoff_roundtrip_no_information_loss(tmp_path: Path):
    env = write_stage_artifact(
        tmp_path,
        stage="worker_a",
        payload={"values": [1, 2, 3], "decision_hint": "SUPPORTED"},
        summary={"n": 3},
    )
    assert "path" in env and "content_hash" in env
    full = read_stage_artifact(env)
    assert full["values"] == [1, 2, 3]
    assert information_loss_from_envelopes([env]) is False


def test_missing_artifact_counts_as_information_loss(tmp_path: Path):
    env = write_stage_artifact(tmp_path, stage="x", payload={"ok": True})
    Path(env["path"]).unlink()
    assert information_loss_from_envelopes([env]) is True
