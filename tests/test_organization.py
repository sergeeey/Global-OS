from __future__ import annotations

import pytest

from global_os.cognition.decomposition import build_repo_audit_dag
from global_os.cognition.organization import (
    GoalDriftDetector,
    OrganizationCompiler,
    OrganizationError,
    OrganizationTopology,
)
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
    assert graph["hypothesis_status"] == "UNPROVEN"
    assert len(graph["workers"]) == 3
    parent_caps = set(graph["parent"]["authority"]["capabilities"])
    for worker in graph["workers"]:
        assert set(worker["authority"]["capabilities"]).issubset(parent_caps)
        assert worker["parent"] == graph["parent"]["id"]


def test_org_compiler_three_topologies_no_default_winner(sample_goal):
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal())
    org = OrganizationCompiler(ledger)
    single = org.compile(goal, topology=OrganizationTopology.SINGLE_SOLVER)
    assert single["topology"] == "single_solver"
    assert len(single["units"]) == 1
    assert single["hypothesis_status"] == "UNPROVEN"

    parallel = org.compile(
        goal,
        topology="parallel_workers",
        worker_missions=["a", "b", "c"],
    )
    assert parallel["topology"] == "parallel_workers"
    assert len(parallel["units"]) == 3

    manager = org.compile(goal, topology="manager_workers", worker_missions=["x", "y"])
    assert manager["topology"] == "manager_workers"
    # GOS-I30: compile never asserts measured superiority
    assert manager["hypothesis_status"] != "SUPPORTED"


def test_recursive_hierarchy_fails_closed_not_silent_fallback(sample_goal):
    ledger = EventLedger()
    goal = GoalStore(ledger).create(sample_goal())
    org = OrganizationCompiler(ledger)
    with pytest.raises(OrganizationError, match="CONTRACTED"):
        org.compile(goal, topology=OrganizationTopology.RECURSIVE_HIERARCHY)


def test_goal_drift_explore_to_execute():
    goal = {
        "goal_id": "goal_buy_research",
        "version": 1,
        "objective": {"text": "Исследовать возможность покупки поставщика"},
        "forbidden_outcomes": ["wire payment"],
    }
    detector = GoalDriftDetector()
    clean = detector.detect(
        goal,
        missions=[{"objective": "Собрать evidence по финансовому состоянию"}],
    )
    assert clean == []

    drifted = detector.detect(
        goal,
        missions=[{"objective": "Совершить покупку и оплатить"}],
        action_summaries=["initiate wire payment"],
    )
    assert detector.has_blocking_drift(drifted)
    kinds = {f.kind for f in drifted}
    assert "explore_to_execute" in kinds
    assert "forbidden_outcome_in_mission" in kinds


def test_repo_audit_dag_has_verification_before_report():
    tasks = build_repo_audit_dag("goal_repo_audit_001")
    by_title = {t["title"]: t for t in tasks}
    assert "verification" in by_title
    assert "report" in by_title
    assert by_title["verification"]["task_id"] in by_title["report"]["depends_on"]
