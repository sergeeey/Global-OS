"""Terminal scorer for Challenge-GA fixture — intermediate plans ≠ WIN."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "artifacts" / "pilot" / "challenge_ga" / "target_fixture" / "workload.py"
LOCK_PATH = ROOT / "artifacts" / "pilot" / "challenge_ga" / "LOCK.json"


def _load_workload(path: Path | None = None) -> Any:
    target = path or FIXTURE
    spec = importlib.util.spec_from_file_location("challenge_ga_workload_score", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fixture: {target}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score_terminal_fixture(
    *,
    workload_path: Path | None = None,
    sealed_checksum: int = 7674672,
    ops_budget_max: int = 80000,
) -> dict[str, Any]:
    """Score only sealed terminal criteria (SCORE_RUBRIC)."""
    mod = _load_workload(workload_path)
    items = list(range(400))
    checksum = mod.process_items(items)
    ops = int(mod.last_ops())
    props_ok = True
    for k in (0, 1, 2, 10, 50):
        # Re-import naive reference semantics: empty→0; small n must be stable ints
        got = mod.process_items(list(range(k)))
        if not isinstance(got, int):
            props_ok = False
            break
        if k == 0 and got != 0:
            props_ok = False
            break

    win = (
        checksum == sealed_checksum
        and ops <= ops_budget_max
        and props_ok
    )
    return {
        "win": win,
        "checksum": checksum,
        "sealed_checksum": sealed_checksum,
        "ops": ops,
        "ops_budget_max": ops_budget_max,
        "property_suite_ok": props_ok,
        "reason": "STOP_SUCCESS" if win else "terminal_criteria_unmet",
    }
