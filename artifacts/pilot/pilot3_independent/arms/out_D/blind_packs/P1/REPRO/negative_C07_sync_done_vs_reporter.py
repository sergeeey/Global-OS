#!/usr/bin/env python3
"""NEGATIVE probe C07: sync pass→done vs flow pass→reporter.

Documents intentional dual-model behavior rather than a silent defect.
sync_issue_state maps gate pass → issue status done (tested).
build_issue_flow_plan with status=in_progress + last_run_status=pass → reporter.

Not asserted as defect: both behaviors are covered by unit tests as designed.
Retained as REJECTED material-defect claim (design dual-path, not breakage).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.issue_flow import build_issue_flow_plan
from workflow_controller.issue_runner import run_issue_gates_from_issue
from workflow_controller.issue_state import sync_issue_state
from workflow_controller.models import IssueExecutionModel, IssueModel

ISSUE = ROOT / "tests" / "fixtures" / "issues" / "clean-issue.json"


def main() -> int:
    issue = IssueModel.model_validate_json(ISSUE.read_text(encoding="utf-8"))
    run = run_issue_gates_from_issue(issue, issue_file=ISSUE)
    synced = sync_issue_state(issue, final_run=run)
    plan_synced = build_issue_flow_plan(synced)

    in_progress_pass = issue.model_copy(
        update={
            "status": "in_progress",
            "execution": IssueExecutionModel(
                last_run_status="pass",
                last_run_reason="all issue gates passed",
            ),
        }
    )
    plan_in_progress = build_issue_flow_plan(in_progress_pass)

    print("synced.status=", synced.status, "plan.next=", plan_synced.next_stage)
    print(
        "in_progress+pass plan.next=",
        plan_in_progress.next_stage,
    )
    print("REJECTED_AS_DEFECT: dual-path is test-covered intentional behavior")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
