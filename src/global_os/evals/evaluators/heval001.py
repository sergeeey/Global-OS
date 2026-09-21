"""H-EVAL-001 synthetic harness — calibrated stack vs raw LLM judge.

GOS-I24: judge cannot validate itself. No magic κ threshold.
Verdict stays INCONCLUSIVE_NEEDS_REAL_MODEL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    ground_truth_pass: bool
    deterministic_pass: bool | None
    raw_judge_pass: bool
    calibrated_judge_pass: bool


# Synthetic escape/error rates — not empirical claims
CASES: tuple[EvalCase, ...] = (
    EvalCase("c1", True, True, True, True),
    EvalCase("c2", True, True, False, True),  # raw judge false negative
    EvalCase("c3", False, False, True, False),  # raw judge false positive
    EvalCase("c4", False, None, True, False),  # no det; calibrated catches
    EvalCase("c5", True, None, True, True),
)


def _escaped(stack: str, case: EvalCase) -> bool:
    """Escaped error = false accept of a failing case."""
    if case.ground_truth_pass:
        return False
    if stack == "raw_judge":
        return case.raw_judge_pass
    if stack == "deterministic_only":
        if case.deterministic_pass is None:
            return True  # no check → escape
        return case.deterministic_pass
    # calibrated: det if present else calibrated judge
    if case.deterministic_pass is not None:
        return case.deterministic_pass  # if det says pass on fail → escape
    return case.calibrated_judge_pass


def summarize_h_eval_001() -> dict[str, Any]:
    stacks = ("raw_judge", "deterministic_only", "calibrated_stack")
    escapes = {
        s: sum(1 for c in CASES if _escaped(s if s != "calibrated_stack" else "calibrated", c))
        for s in stacks
    }
    # fix calibrated key
    escapes["calibrated_stack"] = sum(
        1 for c in CASES if _escaped("calibrated", c)
    )
    return {
        "id": "H-EVAL-001",
        "hypothesis": (
            "Calibrated evaluator stack (deterministic + judge calibration + bias probes) "
            "reduces escaped errors vs raw LLM judge."
        ),
        "fidelity": "synthetic_deterministic",
        "preregistered_at": "2026-09-21",
        "ran_at": datetime.now(UTC).isoformat(),
        "cases": [asdict(c) for c in CASES],
        "escaped_errors": escapes,
        "gos_i24": "judge_self_validation_forbidden",
        "kappa_threshold": None,
        "synthetic_hint_calibrated_better": escapes["calibrated_stack"] < escapes["raw_judge"],
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "note": "No constitutional κ; harness is plumbing only.",
    }
