from __future__ import annotations

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.cognition.organization import OrganizationCompiler
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore


def test_manager_workers_child_authority_subset(sample_goal):
    ledger = EventLedger()
    goals = GoalStore(ledger)
    goal = goals.create(sample_goal())
    org = OrganizationCompiler(ledger)
    graph = org.compile_manager_workers(
        goal,
        worker_missions=["architecture", "testing", "verification"],
        budget_usd=10.0,
        budget_tokens=10000,
    )
    assert graph["topology"] == "manager_workers"
    assert len(graph["workers"]) == 3
    parent_caps = set(graph["parent"]["authority"]["capabilities"])
    for worker in graph["workers"]:
        assert set(worker["authority"]["capabilities"]).issubset(parent_caps)
        assert worker["parent"] == graph["parent"]["id"]


def test_repo_audit_dag_has_verification_before_report():
    tasks = build_repo_audit_dag("goal_repo_audit_001")
    by_title = {t["title"]: t for t in tasks}
    assert "verification" in by_title
    assert "report" in by_title
    assert by_title["verification"]["task_id"] in by_title["report"]["depends_on"]
