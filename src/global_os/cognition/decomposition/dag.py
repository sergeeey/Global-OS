"""Task DAG builder — Problem → tasks without executing agents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from global_os.common.hashing import new_id
from global_os.contracts.validate import validate


def build_repo_audit_dag(goal_id: str) -> list[dict[str, Any]]:
    """Canonical first killer-use-case task graph."""
    titles = [
        ("architecture", []),
        ("implementation", ["architecture"]),
        ("testing", ["implementation"]),
        ("runtime", ["implementation"]),
        ("supply_chain", ["architecture"]),
        ("verification", ["testing", "runtime", "supply_chain"]),
        ("report", ["verification"]),
    ]
    id_by_key: dict[str, str] = {}
    tasks: list[dict[str, Any]] = []
    for key, deps in titles:
        tid = new_id("task")
        id_by_key[key] = tid
        task = {
            "task_id": tid,
            "schema_version": "0.1.0",
            "goal_id": goal_id,
            "title": key,
            "state": "PENDING",
            "depends_on": [id_by_key[d] for d in deps],
            "output_artifact_refs": [],
        }
        validate(task, "task.schema.json")
        tasks.append(task)
    return deepcopy(tasks)
