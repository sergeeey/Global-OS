"""Pilot 3 Pack regression probes against Paperclip workflow-controller.

Run from the Pack checkout (pre-fix expected FAIL for these cases):

  cd /tmp/pilot/p3-arm-A/tools/workflow-controller
  PYTHONPATH=. python3 /workspace/artifacts/pilot/pilot3_independent/arms/out_P/REPRO/test_pilot3_arm_a_regressions.py

After applying FIXES.md patches, the same file should pass.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path("/tmp/pilot/p3-arm-A/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.event_log import verify_event_log
from workflow_controller.issue_flow import build_issue_flow_plan
from workflow_controller.issue_runner import run_issue_gates
from workflow_controller.issue_state import sync_issue_state
from workflow_controller.mcp_tools import WorkflowToolService
from workflow_controller.models import IssueExecutionModel, IssueModel
from workflow_controller.security_gate import verify_security_scans
from workflow_controller.tool_policy import PATH_ARGUMENT_NAMES, ToolPolicy, evaluate_tool_request


FIXTURE_ISSUE = ROOT / "tests" / "fixtures" / "issues" / "clean-issue.json"


class Pilot3ArmARegressions(unittest.TestCase):
    def test_event_log_accepts_artifact_gate_fail(self) -> None:
        """F1: legitimate artifact-gate FAIL must verify_event_log as pass."""
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            project.mkdir()
            (project / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 15, "failed": 2}}),
                encoding="utf-8",
            )
            (project / "coverage.xml").write_text(
                '<?xml version="1.0"?><coverage line-rate="0.9"></coverage>',
                encoding="utf-8",
            )
            (project / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            event_log = Path(tmp) / "events.jsonl"

            run = run_issue_gates(issue_id="BUG-1", project_dir=project, event_log=event_log)
            self.assertEqual(run.final.status, "fail")

            verdict = verify_event_log(event_log=event_log, expected_issue_id="BUG-1")
            self.assertEqual(
                verdict.status,
                "pass",
                msg=f"verify_event_log false-failed legitimate traffic: {verdict.reason}",
            )

    def test_output_file_is_policy_enforced(self) -> None:
        """F2: output_file outside allowed roots must be blocked (and not written)."""
        self.assertIn("output_file", PATH_ARGUMENT_NAMES)

        with tempfile.TemporaryDirectory() as allowed:
            with tempfile.TemporaryDirectory() as denied:
                policy = ToolPolicy(allowed_roots=(Path(allowed), Path.cwd()))
                decision = evaluate_tool_request(
                    "workflow_sync_issue_state",
                    {
                        "issue_file": str(FIXTURE_ISSUE),
                        "output_file": str(Path(denied) / "pwned.json"),
                    },
                    policy=policy,
                )
                self.assertEqual(decision.action, "block")

                service = WorkflowToolService(policy=policy)
                out = Path(denied) / "escape.json"
                response = service.sync_issue_state(
                    issue_file=str(FIXTURE_ISSUE),
                    output_file=str(out),
                )
                self.assertEqual(response["policy"]["action"], "block")
                self.assertFalse(out.exists())

    def test_semgrep_run_exit_1_with_note_only_does_not_fail_gate(self) -> None:
        """F3: semgrep exit 1 + note-only SARIF must not fail when block_levels exclude note."""
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            sarif = project / "semgrep.sarif"
            th = project / "th.jsonl"
            th.write_text("", encoding="utf-8")
            payload = {
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "Semgrep", "rules": []}},
                        "results": [
                            {
                                "ruleId": "x",
                                "level": "note",
                                "message": {"text": "informational"},
                            }
                        ],
                    }
                ],
            }

            def fake_run(command, **kwargs):
                Path(command[command.index("--sarif-output") + 1]).write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, returncode=1, stdout="", stderr="findings")

            with patch(
                "workflow_controller.security_gate.shutil.which",
                return_value="/usr/bin/semgrep",
            ), patch(
                "workflow_controller.security_gate._run_command",
                side_effect=fake_run,
            ):
                verdict = verify_security_scans(
                    issue_id="BUG-2",
                    project_dir=project,
                    run_semgrep=True,
                    semgrep_sarif=sarif,
                    trufflehog_json=th,
                    semgrep_block_levels=("error", "warning"),
                )

            self.assertEqual(
                verdict.status,
                "pass",
                msg=f"false-positive security fail: {verdict.reason} checks={[ (c.name,c.status) for c in verdict.checks ]}",
            )

    def test_trufflehog_run_exit_nonzero_defers_to_jsonl_policy(self) -> None:
        """F5: trufflehog non-zero exit with unverified findings must honor block_unknown=False."""
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            sarif = project / "semgrep.sarif"
            th = project / "th.jsonl"
            sarif.write_text(
                json.dumps(
                    {
                        "version": "2.1.0",
                        "runs": [
                            {
                                "tool": {"driver": {"name": "Semgrep", "rules": []}},
                                "results": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            finding = json.dumps({"DetectorName": "X", "Verified": False, "Raw": "x"}) + "\n"

            def fake_run(command, **kwargs):
                return subprocess.CompletedProcess(command, returncode=183, stdout=finding, stderr="")

            with patch(
                "workflow_controller.security_gate.shutil.which",
                return_value="/usr/bin/trufflehog",
            ), patch(
                "workflow_controller.security_gate._run_command",
                side_effect=fake_run,
            ):
                verdict = verify_security_scans(
                    issue_id="BUG-5",
                    project_dir=project,
                    semgrep_sarif=sarif,
                    run_trufflehog=True,
                    trufflehog_json=th,
                    block_trufflehog_unknown=False,
                )

            self.assertEqual(
                verdict.status,
                "pass",
                msg=f"false-positive security fail: {verdict.reason}",
            )

    def test_sync_pass_does_not_skip_reporter_devops(self) -> None:
        """F4: gate pass must not mark issue done (skips Reporter/DevOps in plan)."""
        issue = IssueModel.model_validate_json(FIXTURE_ISSUE.read_text(encoding="utf-8"))
        run = run_issue_gates(
            issue_id=issue.issue_id,
            project_dir=(FIXTURE_ISSUE.parent / issue.output_location).resolve(),
            semgrep_sarif=(FIXTURE_ISSUE.parent / ".." / "clean-project" / "semgrep.sarif").resolve(),
            trufflehog_json=(FIXTURE_ISSUE.parent / ".." / "clean-project" / "trufflehog.jsonl").resolve(),
        )
        self.assertEqual(run.final.status, "pass")
        synced = sync_issue_state(issue, final_run=run)
        self.assertNotEqual(
            synced.status,
            "done",
            msg="sync_issue_state must not jump to done before Reporter/DevOps",
        )
        plan = build_issue_flow_plan(synced)
        self.assertEqual(plan.next_stage, "reporter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
