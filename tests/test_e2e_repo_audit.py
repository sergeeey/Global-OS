from __future__ import annotations

from pathlib import Path

from global_os.cognition.organization import OrganizationCompiler
from global_os.cognition.workers import WorkerRuntime, WorkerSpec
from global_os.runtime.events import EventLedger
from global_os.runtime.goals import GoalStore
from global_os.verification import ResultClass, VerificationRequest, VerificationRouter
from global_os.world.artifacts import ArtifactStore
from global_os.world.tools import run_repo_audit


def test_e2e_repo_audit_goal_org_workers(sample_goal, tmp_path: Path):
    ledger = EventLedger()
    goals = GoalStore(ledger)
    goal = goals.create(sample_goal(goal_id="goal_e2e_audit"))
    org = OrganizationCompiler(ledger).compile_manager_workers(
        goal,
        worker_missions=["architecture", "testing", "verification"],
        budget_usd=5.0,
        budget_tokens=5000,
    )
    assert len(org["workers"]) == 3

    root = Path(__file__).resolve().parents[1]
    audit = run_repo_audit(root)
    assert audit["modified_target"] is False

    store = ArtifactStore(tmp_path / "art")
    workers = WorkerRuntime(ledger, store)
    parent_caps = frozenset(goal["authority"]["capabilities"])
    wid = workers.spawn(
        WorkerSpec(
            mission="architecture",
            capabilities=frozenset({"filesystem.read"}),
            parent_capabilities=parent_caps,
            fn=lambda _a: {"audit_findings": len(audit["findings"])},
        ),
        tenant_id=goal["tenant_id"],
        workspace_id=goal["workspace_id"],
        goal_id=goal["goal_id"],
    )
    result = workers.run(
        wid,
        {"audit": audit},
        tenant_id=goal["tenant_id"],
        workspace_id=goal["workspace_id"],
        goal_id=goal["goal_id"],
    )
    assert result.artifact_digest

    vout = VerificationRouter().route(
        VerificationRequest(
            result_class=ResultClass.NUMERIC,
            payload={
                "expected": len(audit["findings"]),
                "actual": result.output["audit_findings"],
            },
        )
    )
    assert vout.passed is True
