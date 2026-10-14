"""Active falsifiers — counterexamples before SUCCESS (Verification Plane helper).

Not a Kernel / prosecutor agent. Concrete observations only; no LLM oracle.
Absence of a found counterexample never upgrades unknown → met.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from global_os.runtime.preprod.goal_postconditions import (
    expected_write_paths_for_criterion,
)
from global_os.world.tools.workspace_io import resolve_under

_EXACT_LINE_RE = re.compile(r"exact\s+line\s+([A-Za-z0-9_.\-]+)", re.IGNORECASE)


class FalsificationOutcome(str, Enum):
    FALSIFIED = "falsified"
    NOT_FALSIFIED = "not_falsified"
    UNOBSERVABLE = "unobservable"


@dataclass(frozen=True)
class FalsificationResult:
    criterion_id: str
    outcome: FalsificationOutcome
    reason: str
    observation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "outcome": self.outcome.value,
            "reason": self.reason,
            "observation": dict(self.observation),
        }


def _criterion_entries(goal: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for c in goal.get("success_criteria") or []:
        if isinstance(c, str):
            out.append((c, c))
            continue
        cid = str(c.get("id") or "")
        desc = str(c.get("description") or "")
        if cid:
            out.append((cid, desc))
    return out


def _exact_line_marker(description: str) -> str | None:
    m = _EXACT_LINE_RE.search(description or "")
    return m.group(1) if m else None


def falsify_filesystem_criterion(
    *,
    criterion_id: str,
    description: str,
    target: Path,
) -> FalsificationResult:
    """Seek a concrete filesystem counterexample for a write/accept criterion."""
    expected = expected_write_paths_for_criterion(description)
    if not expected:
        return FalsificationResult(
            criterion_id=criterion_id,
            outcome=FalsificationOutcome.NOT_FALSIFIED,
            reason="no_concrete_filename_token",
            observation={},
        )

    if not target.exists():
        return FalsificationResult(
            criterion_id=criterion_id,
            outcome=FalsificationOutcome.UNOBSERVABLE,
            reason="target_missing",
            observation={"target": str(target), "expected": expected},
        )
    if not target.is_dir():
        return FalsificationResult(
            criterion_id=criterion_id,
            outcome=FalsificationOutcome.UNOBSERVABLE,
            reason="target_not_directory",
            observation={"target": str(target), "expected": expected},
        )
    if not os_access_readable(target):
        return FalsificationResult(
            criterion_id=criterion_id,
            outcome=FalsificationOutcome.UNOBSERVABLE,
            reason="target_not_readable",
            observation={"target": str(target), "expected": expected},
        )

    marker = _exact_line_marker(description)
    for rel in expected:
        path = resolve_under(target, rel)
        if path is None:
            return FalsificationResult(
                criterion_id=criterion_id,
                outcome=FalsificationOutcome.FALSIFIED,
                reason="expected_path_escape_or_invalid",
                observation={"expected": expected, "path": rel},
            )
        if not path.is_file():
            return FalsificationResult(
                criterion_id=criterion_id,
                outcome=FalsificationOutcome.FALSIFIED,
                reason="required_file_absent",
                observation={"expected": expected, "path": rel},
            )
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            return FalsificationResult(
                criterion_id=criterion_id,
                outcome=FalsificationOutcome.UNOBSERVABLE,
                reason=f"read_failed:{exc}",
                observation={"path": rel},
            )
        if path.stat().st_size == 0 or not text.strip():
            return FalsificationResult(
                criterion_id=criterion_id,
                outcome=FalsificationOutcome.FALSIFIED,
                reason="required_file_empty",
                observation={"path": rel},
            )
        if marker is not None and marker not in text:
            return FalsificationResult(
                criterion_id=criterion_id,
                outcome=FalsificationOutcome.FALSIFIED,
                reason="exact_line_marker_absent",
                observation={"path": rel, "marker": marker},
            )

    return FalsificationResult(
        criterion_id=criterion_id,
        outcome=FalsificationOutcome.NOT_FALSIFIED,
        reason="no_filesystem_counterexample",
        observation={"expected": expected, "marker": marker},
    )


def os_access_readable(path: Path) -> bool:
    try:
        next(path.iterdir(), None)
        return True
    except OSError:
        return False


def run_filesystem_falsifiers(
    goal: dict[str, Any],
    target: Path | None,
) -> dict[str, FalsificationResult]:
    """Run filesystem falsifiers for criteria with concrete FIX_*/ACCEPT_* tokens."""
    results: dict[str, FalsificationResult] = {}
    if target is None:
        for cid, desc in _criterion_entries(goal):
            expected = expected_write_paths_for_criterion(desc)
            if expected:
                results[cid] = FalsificationResult(
                    criterion_id=cid,
                    outcome=FalsificationOutcome.UNOBSERVABLE,
                    reason="target_not_provided",
                    observation={"expected": expected},
                )
        return results

    for cid, desc in _criterion_entries(goal):
        expected = expected_write_paths_for_criterion(desc)
        if not expected:
            continue
        results[cid] = falsify_filesystem_criterion(
            criterion_id=cid, description=desc, target=target
        )
    return results


def falsification_results_as_dicts(
    results: dict[str, FalsificationResult],
) -> dict[str, dict[str, Any]]:
    return {cid: r.to_dict() for cid, r in results.items()}
