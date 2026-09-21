from __future__ import annotations

import pytest

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.cognition.environment import EnvironmentCompiler, EnvironmentCompilerError
from global_os.cognition.organization import OrganizationCompiler
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore


def test_environment_compiler_from_goal_org_task(sample_goal):
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal())
    org = OrganizationCompiler(ledger).compile_manager_workers(
        goal,
        worker_missions=["architecture", "testing"],
        budget_usd=4.0,
        budget_tokens=8000,
    )
    tasks = build_repo_audit_dag(goal["goal_id"])
    worker = org["workers"][0]
    env = EnvironmentCompiler().compile(
        goal=goal, org_unit=worker, task=tasks[0], verification_tier=2
    )
    assert env["goal_id"] == goal["goal_id"]
    assert env["org_unit_id"] == worker["id"]
    assert set(env["tools"]["allow"]).issubset(set(goal["authority"]["capabilities"]))


def test_environment_compiler_rejects_authority_expansion(sample_goal):
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal())
    bad_org = {
        "id": "org_bad",
        "authority": {"capabilities": ["filesystem.read", "email.send"]},
        "budget": {"usd": 1, "tokens": 100},
        "output_contract": "x",
    }
    task = {"task_id": "task_x", "title": "architecture"}
    with pytest.raises(EnvironmentCompilerError, match="GOS-I04"):
        EnvironmentCompiler().compile(goal=goal, org_unit=bad_org, task=task)
