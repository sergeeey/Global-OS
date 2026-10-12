"""Regression tests for Pilot3 Arm B confirmed defects.

These assert *correct* post-fix behavior. On unpatched workflow-controller
they FAIL (red). After applying FIXES.md patches in the Paperclip tree they PASS.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

WC_ROOT = Path("/tmp/pilot/p3-arm-B/tools/workflow-controller")
sys.path.insert(0, str(WC_ROOT))

from workflow_controller.artifact_gate import verify_artifacts
from workflow_controller.event_log import verify_event_log
from workflow_controller.issue_runner import run_issue_gates
from workflow_controller.mcp_tools import WorkflowToolService
from workflow_controller.tool_policy import PATH_ARGUMENT_NAMES, ToolPolicy, evaluate_tool_request


class B01OutputFilePolicyBypass(unittest.TestCase):
    """output_file must be constrained by allowed_roots."""

    def test_output_file_is_a_path_argument(self) -> None:
        self.assertIn("output_file", PATH_ARGUMENT_NAMES)

    def test_blocks_output_file_outside_allowed_roots(self) -> None:
        with tempfile.TemporaryDirectory() as allowed, tempfile.TemporaryDirectory() as denied:
            decision = evaluate_tool_request(
                "workflow_sync_issue_state",
                {
                    "issue_file": str(Path(allowed) / "issue.json"),
                    "output_file": str(Path(denied) / "pwned.json"),
                },
                policy=ToolPolicy(allowed_roots=(Path(allowed),)),
            )
        self.assertEqual(decision.action, "block")
        self.assertIn("outside allowed roots", decision.reason)

    def test_mcp_sync_does_not_write_outside_roots(self) -> None:
        with tempfile.TemporaryDirectory() as allowed, tempfile.TemporaryDirectory() as denied:
            allowed_root = Path(allowed)
            denied_root = Path(denied)
            project = allowed_root / "project"
            project.mkdir()
            self._write_clean_project(project)
            issue_file = allowed_root / "issue.json"
            issue_file.write_text(
                json.dumps(self._issue(str(project), project)),
                encoding="utf-8",
            )
            outside = denied_root / "pwned-issue.json"
            service = WorkflowToolService(policy=ToolPolicy(allowed_roots=(allowed_root,)))
            response = service.sync_issue_state(
                issue_file=str(issue_file),
                output_file=str(outside),
            )
            self.assertEqual(response["policy"]["action"], "block")
            self.assertFalse(outside.exists())

    def _write_clean_project(self, project: Path) -> None:
        (project / "test-results.json").write_text(
            json.dumps({"summary": {"passed": 15, "failed": 0}}),
            encoding="utf-8",
        )
        (project / "coverage.xml").write_text(
            '<?xml version="1.0" ?><coverage line-rate="0.9"></coverage>',
            encoding="utf-8",
        )
        (project / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
        (project / "semgrep.sarif").write_text(
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
        (project / "trufflehog.jsonl").write_text("", encoding="utf-8")

    def _issue(self, output_location: str, project: Path) -> dict:
        return {
            "issue_id": "WRT-1",
            "title": "WRT-1: write escape",
            "goal": "g",
            "requirements": ["r"],
            "tech_stack": {"Language": "Python"},
            "output_location": output_location,
            "acceptance_criteria": ["a"],
            "required_artifacts": ["test-results.json", "coverage.xml", "README.md"],
            "assigned_to": "Builder Bot",
            "status": "todo",
            "execution": {
                "semgrep_sarif": str(project / "semgrep.sarif"),
                "trufflehog_json": str(project / "trufflehog.jsonl"),
            },
        }


class B02NestedIssuePathBypass(unittest.TestCase):
    """Paths inside issue JSON must be checked against allowed_roots before gate run."""

    def test_sync_blocks_output_location_outside_roots(self) -> None:
        with tempfile.TemporaryDirectory() as allowed, tempfile.TemporaryDirectory() as denied:
            allowed_root = Path(allowed)
            denied_root = Path(denied)
            secret = denied_root / "secret-project"
            secret.mkdir()
            (secret / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 15, "failed": 0}}),
                encoding="utf-8",
            )
            (secret / "coverage.xml").write_text(
                '<?xml version="1.0" ?><coverage line-rate="0.9"></coverage>',
                encoding="utf-8",
            )
            (secret / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            (secret / "semgrep.sarif").write_text(
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
            (secret / "trufflehog.jsonl").write_text("", encoding="utf-8")
            issue_file = allowed_root / "issue.json"
            issue_file.write_text(
                json.dumps(
                    {
                        "issue_id": "ESC-1",
                        "title": "ESC-1: escape",
                        "goal": "escape roots",
                        "requirements": ["x"],
                        "tech_stack": {"Language": "Python"},
                        "output_location": str(secret),
                        "acceptance_criteria": ["x"],
                        "required_artifacts": ["test-results.json"],
                        "assigned_to": "Builder Bot",
                        "status": "todo",
                        "execution": {
                            "semgrep_sarif": str(secret / "semgrep.sarif"),
                            "trufflehog_json": str(secret / "trufflehog.jsonl"),
                        },
                    }
                ),
                encoding="utf-8",
            )
            service = WorkflowToolService(policy=ToolPolicy(allowed_roots=(allowed_root,)))
            response = service.sync_issue_state(
                issue_file=str(issue_file),
                output_file=str(allowed_root / "out.json"),
            )
            self.assertEqual(response["policy"]["action"], "block")
            self.assertNotIn("result", response)


class B03MissingFailedDefaultsPass(unittest.TestCase):
    """README requires summary.failed; missing field must not pass."""

    def test_missing_failed_field_fails_artifact_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 15}}),
                encoding="utf-8",
            )
            (project / "coverage.xml").write_text(
                '<?xml version="1.0" ?><coverage line-rate="0.9"></coverage>',
                encoding="utf-8",
            )
            (project / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            verdict = verify_artifacts(issue_id="BLI-2", project_dir=project)
        self.assertEqual(verdict.status, "fail")
        test_check = next(c for c in verdict.checks if c.name == "test-results.json")
        self.assertEqual(test_check.status, "fail")


class B04EventLogRejectsArtifactFail(unittest.TestCase):
    """Legitimate artifact-gate fail event logs must verify."""

    def test_artifact_fail_event_log_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 1, "failed": 2}}),
                encoding="utf-8",
            )
            (project / "coverage.xml").write_text(
                '<?xml version="1.0" ?><coverage line-rate="0.9"></coverage>',
                encoding="utf-8",
            )
            (project / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            event_log = project / "events.jsonl"
            run = run_issue_gates(issue_id="BLI-2", project_dir=project, event_log=event_log)
            self.assertEqual(run.final.status, "fail")
            self.assertEqual(run.final.reason, "artifact gate fail")
            verdict = verify_event_log(event_log=event_log, expected_issue_id="BLI-2")
        self.assertEqual(verdict.status, "pass", msg=verdict.reason)


class B05EmptyAllowListAllowsAll(unittest.TestCase):
    """Empty allowed_tools must not silently allow unknown tools."""

    def test_empty_allowed_tools_blocks_unknown(self) -> None:
        decision = evaluate_tool_request(
            "shell",
            {"command": "whoami"},
            policy=ToolPolicy(allowed_tools=(), allowed_roots=(Path("/tmp"),)),
        )
        self.assertEqual(decision.action, "block")


if __name__ == "__main__":
    unittest.main()
