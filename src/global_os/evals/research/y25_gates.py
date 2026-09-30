"""Y25 prereg / isolation / unseen-variant gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from global_os.evals.trust.t1_protocol import repo_root


def y25_root(root: Path | None = None) -> Path:
    return (root or repo_root()) / "artifacts" / "y25"


def load_prereg(root: Path | None = None) -> dict[str, Any]:
    path = y25_root(root) / "Y25-PREREG.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_holdout_manifest(root: Path | None = None) -> dict[str, Any]:
    path = y25_root(root) / "sealed" / "HOLDOUT_MANIFEST.json"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_prereg_locked(root: Path | None = None) -> dict[str, Any]:
    prereg = load_prereg(root)
    if prereg.get("status") != "PREREG_LOCKED":
        raise ValueError("Y25 prereg not PREREG_LOCKED")
    return prereg


def assert_y24_closed_not_rescued(root: Path | None = None) -> None:
    closed = (root or repo_root()) / "artifacts" / "y24" / "Y24_CLOSED.json"
    data = json.loads(closed.read_text(encoding="utf-8"))
    if data.get("status") != "CAMPAIGN_CLOSED":
        raise ValueError("Y24 must be CAMPAIGN_CLOSED before Y25 proceeds")
    if data.get("post_hoc_y24_rescue_forbidden") is not True:
        raise ValueError("Y24 rescue must remain forbidden")


def memory_pair_valid(first: dict[str, Any], variant: dict[str, Any]) -> bool:
    if first.get("failure_class") != variant.get("failure_class") or not first.get(
        "failure_class"
    ):
        return False
    if first.get("task_id") == variant.get("task_id"):
        return False
    if first.get("patch_ref") and first.get("patch_ref") == variant.get("patch_ref"):
        return False
    if first.get("commit_sha") and first.get("commit_sha") == variant.get("commit_sha"):
        return False
    # Prefer different repos when both present
    if first.get("repo_url") and variant.get("repo_url"):
        if first.get("repo_url") == variant.get("repo_url") and first.get(
            "patch_ref"
        ) == variant.get("patch_ref"):
            return False
    return first.get("memory_role") == "first" and variant.get("memory_role") == (
        "unseen_variant"
    )


def refuse_arm_execution(root: Path | None = None) -> None:
    assert_prereg_locked(root)
    assert_y24_closed_not_rescued(root)
    man = load_holdout_manifest(root)
    status = str(man.get("status") or "")
    if status != "UNSEALED_FOR_EXECUTION":
        raise RuntimeError(
            "Y25 arm execution refused: holdout not UNSEALED_FOR_EXECUTION "
            "(corpus pairs → seal → SHA freeze → W0/W1 stubs → attestation first)"
        )
    att = y25_root(root) / "ISOLATION_ATTESTATION.md"
    text = att.read_text(encoding="utf-8")
    if "I did not access artifacts/y25/sealed" not in text:
        raise RuntimeError("Y25 arm execution refused: isolation attestation blank")
