"""Y24 pre-execution gates: holdout seal + isolation + no threshold fishing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from global_os.evals.trust.t1_protocol import repo_root


def y24_root(root: Path | None = None) -> Path:
    return (root or repo_root()) / "artifacts" / "y24"


def load_prereg(root: Path | None = None) -> dict[str, Any]:
    path = y24_root(root) / "Y24-PREREG.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("Y24-PREREG.json must be object")
    return raw


def load_holdout_manifest(root: Path | None = None) -> dict[str, Any]:
    path = y24_root(root) / "sealed" / "HOLDOUT_MANIFEST.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("HOLDOUT_MANIFEST.json must be object")
    return raw


def assert_prereg_locked(root: Path | None = None) -> dict[str, Any]:
    prereg = load_prereg(root)
    if prereg.get("status") != "PREREG_LOCKED":
        raise ValueError("Y24 prereg not PREREG_LOCKED")
    return prereg


def assert_arms_not_started(root: Path | None = None) -> None:
    prereg = load_prereg(root)
    if prereg.get("arms_started") is not False:
        raise ValueError("Y24 arms_started must be false until execution stage")


def assert_holdout_not_leaked_to_arm_builders(root: Path | None = None) -> None:
    """Fail closed if sealed holdout already carries labels while still NOT_SEALED
    inconsistently, or if execution is attempted too early.
    """
    man = load_holdout_manifest(root)
    status = str(man.get("status") or "")
    if status == "NOT_SEALED_YET" and man.get("tasks"):
        raise ValueError(
            "holdout manifest has tasks but status NOT_SEALED_YET — "
            "finish seal protocol before populating execution views"
        )
    if man.get("unsealed_for_execution") is True and status != "UNSEALED_FOR_EXECUTION":
        raise ValueError("unsealed_for_execution flag inconsistent with status")


def refuse_arm_execution(root: Path | None = None) -> None:
    """Hard refuse until holdout is explicitly unsealed for execution."""
    assert_prereg_locked(root)
    assert_holdout_not_leaked_to_arm_builders(root)
    man = load_holdout_manifest(root)
    status = str(man.get("status") or "")
    if status in {"NOT_SEALED_YET", "FROZEN_UNSEEN"}:
        raise RuntimeError(
            "Y24 arm execution refused: holdout not UNSEALED_FOR_EXECUTION "
            "(complete corpus → stratum score → seal → SHA freeze → stubs → "
            "isolation attestation first)"
        )
    if status != "UNSEALED_FOR_EXECUTION":
        raise RuntimeError(f"Y24 arm execution refused: unexpected holdout status {status}")
    att = y24_root(root) / "ISOLATION_ATTESTATION.md"
    text = att.read_text(encoding="utf-8")
    if "I did not access artifacts/y24/sealed" not in text:
        raise RuntimeError(
            "Y24 arm execution refused: isolation attestation blank/missing"
        )


def memory_pair_valid(first: dict[str, Any], variant: dict[str, Any]) -> bool:
    """Unseen variant: same failure_class, different task identity; not identical patch."""
    if first.get("failure_class") != variant.get("failure_class"):
        return False
    if not first.get("failure_class"):
        return False
    if first.get("task_id") == variant.get("task_id"):
        return False
    if first.get("patch_ref") and first.get("patch_ref") == variant.get("patch_ref"):
        return False
    if first.get("memory_pair_id") != variant.get("memory_pair_id"):
        return False
    return (
        first.get("memory_role") == "first"
        and variant.get("memory_role") == "unseen_variant"
    )
