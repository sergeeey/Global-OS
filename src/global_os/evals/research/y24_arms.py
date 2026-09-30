"""Y24 arm stubs A/B/C — refuse execution until gates pass; no Trust Kernel edits."""

from __future__ import annotations

from typing import Any

from global_os.evals.research.y24_cost import LEDGER_FIELDS
from global_os.evals.research.y24_gates import refuse_arm_execution

ARM_DEFS = {
    "A": "strong_simple_verifier_no_memory",
    "B": "llm_verifier_no_durable_memory",
    "C": "adaptive_verifier_benign_calibration_memory_bounded_escalation",
}


def empty_ledger(task_id: str, arm_id: str) -> dict[str, Any]:
    if arm_id not in ARM_DEFS:
        raise ValueError(f"unknown arm {arm_id}")
    out: dict[str, Any] = {"task_id": task_id, "arm_id": arm_id}
    for field in LEDGER_FIELDS:
        out[field] = 0
    out["honest_stop"] = False
    out["cap_hit"] = None
    return out


def run_arm_stub(arm_id: str, task: dict[str, Any]) -> dict[str, Any]:
    """Stub entrypoint: always refuse until unseal + attestation."""
    del task  # unused until execution stage
    if arm_id not in ARM_DEFS:
        raise ValueError(f"unknown arm {arm_id}")
    refuse_arm_execution()
    raise RuntimeError("unreachable: refuse_arm_execution must raise")
