"""Y25 W0/W1 stubs — refuse until holdout unsealed."""

from __future__ import annotations

from typing import Any

from global_os.evals.research.y25_gates import refuse_arm_execution

ARM_DEFS = {
    "W0": "without_memory",
    "W1": "with_memory_dev_first_encounters_only",
}


def empty_ledger(task_id: str, arm_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "arm_id": arm_id,
        "llm_cost_tokens": 0,
        "tool_calls": 0,
        "human_interventions": 0,
        "latency_ms": 0,
        "verification_calls": 0,
        "recovery_overhead_seconds": 0.0,
        "time_to_diagnosis_s": 0.0,
        "false_positive": False,
        "escaped_error": False,
        "task_contained": True,
    }


def run_arm_stub(arm_id: str, task: dict[str, Any]) -> dict[str, Any]:
    if arm_id not in ARM_DEFS:
        raise ValueError(f"unknown arm {arm_id}")
    refuse_arm_execution()
    return empty_ledger(str(task.get("task_id") or ""), arm_id)
