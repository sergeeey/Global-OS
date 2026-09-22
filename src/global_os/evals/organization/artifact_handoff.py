"""Artifact-first handoff — minimal fix for recurring summary information_loss.

Workers persist full stage payloads to durable artifact files; manager receives
refs (+ optional short summary) and can re-read the full payload. This does not
create a new privileged subsystem — it is a process constraint for org evals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from global_os.common.hashing import content_hash, new_id


def write_stage_artifact(
    handoff_dir: Path,
    *,
    stage: str,
    payload: dict[str, Any],
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist full worker payload; return handoff envelope (ref + optional summary)."""
    handoff_dir.mkdir(parents=True, exist_ok=True)
    artifact_id = new_id("haf")
    path = handoff_dir / f"{stage}_{artifact_id}.json"
    body = {
        "artifact_id": artifact_id,
        "stage": stage,
        "payload": payload,
        "content_hash": content_hash(payload),
    }
    path.write_text(json.dumps(body, indent=2, default=str), encoding="utf-8")
    envelope: dict[str, Any] = {
        "artifact_id": artifact_id,
        "stage": stage,
        "path": str(path),
        "content_hash": body["content_hash"],
    }
    if summary is not None:
        envelope["summary"] = summary
    return envelope


def read_stage_artifact(envelope: dict[str, Any]) -> dict[str, Any]:
    """Manager reloads full payload from artifact ref (no silent summary-only path)."""
    path = Path(envelope["path"])
    if not path.exists():
        raise FileNotFoundError(f"handoff artifact missing: {path}")
    body = json.loads(path.read_text(encoding="utf-8"))
    if body.get("content_hash") != envelope.get("content_hash"):
        raise ValueError("handoff artifact hash mismatch")
    if body.get("artifact_id") != envelope.get("artifact_id"):
        raise ValueError("handoff artifact id mismatch")
    payload = body["payload"]
    if not isinstance(payload, dict):
        raise TypeError("handoff artifact payload must be a dict")
    return payload


def information_loss_from_envelopes(envelopes: list[dict[str, Any]]) -> bool:
    """False iff every envelope is reloadable to a full payload."""
    for env in envelopes:
        try:
            payload = read_stage_artifact(env)
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            return True
        if not isinstance(payload, dict) or not payload:
            return True
    return False
