"""Regression tests for Pilot3 Arm C confirmed defects (C01–C06)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workflow_controller.artifact_gate import verify_artifacts
from workflow_controller.cli import _build_parser
from workflow_controller.event_log import verify_event_log
from workflow_controller.issue_runner import run_issue_gates
from workflow_controller.mcp_tools import WorkflowToolService
from workflow_controller.tool_policy import ToolPolicy, evaluate_tool_request

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ISSUE = FIXTURES / "issues" / "clean-issue.json"


class Pilot3ArmCRegressionTests(unittest.TestCase):
    def test_c01_event_log_accepts_artifact_gate_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_dir = root / "project"
            project_dir.mkdir()
            (project_dir / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 10, "failed": 2}}),
                encoding="utf-8",
            )
            (project_dir / "coverage.xml").write_text(
                '<?xml version="1.0" ?><coverage line-rate="0.90"></coverage>',
                encoding="utf-8",
            )
            (project_dir / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            event_log = root / "events.jsonl"

            run = run_issue_gates(issue_id="REG-1", project_dir=project_dir, event_log=event_log)
            self.assertEqual(run.final.status, "fail")
            self.assertEqual(run.final.reason, "artifact gate fail")

            verdict = verify_event_log(event_log=event_log, expected_issue_id="REG-1")
            self.assertEqual(verdict.status, "pass", verdict.reason)

    def test_c02_output_file_outside_roots_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as allowed_tmp:
            with tempfile.TemporaryDirectory() as denied_tmp:
                allowed = Path(allowed_tmp)
                outside = Path(denied_tmp) / "out.json"
                policy = ToolPolicy(allowed_roots=(Path.cwd(), allowed))
                decision = evaluate_tool_request(
                    "workflow_sync_issue_state",
                    {
                        "issue_file": str(ISSUE),
                        "output_file": str(outside),
                        "event_log": str(allowed / "events.jsonl"),
                    },
                    policy=policy,
                )
                self.assertEqual(decision.action, "block")
                self.assertIn("output_file", decision.reason)

                service = WorkflowToolService(policy=policy)
                response = service.sync_issue_state(
                    issue_file=str(ISSUE),
                    output_file=str(outside),
                    event_log=str(allowed / "events.jsonl"),
                )
                self.assertEqual(response["status"], "blocked")
                self.assertFalse(outside.exists())

    def test_c03_empty_allowlist_denies_unknown_tool(self) -> None:
        policy = ToolPolicy(allowed_tools=(), allowed_roots=(Path.cwd(),))
        decision = evaluate_tool_request("shell_exec_anything", {}, policy=policy)
        self.assertEqual(decision.action, "block")
        self.assertIn("not in allow list", decision.reason)

    def test_c04_filesystem_semgrep_config_checked(self) -> None:
        with tempfile.TemporaryDirectory() as allowed_tmp:
            with tempfile.TemporaryDirectory() as denied_tmp:
                policy = ToolPolicy(allowed_roots=(Path(allowed_tmp),))
                outside = Path(denied_tmp) / "evil.yml"
                outside.write_text("rules: []\n", encoding="utf-8")
                project_dir = Path(allowed_tmp) / "project"
                project_dir.mkdir()
                decision = evaluate_tool_request(
                    "workflow_verify_security",
                    {
                        "project_dir": str(project_dir),
                        "semgrep_config": str(outside),
                        "run_semgrep": True,
                    },
                    policy=policy,
                )
                self.assertEqual(decision.action, "block")
                self.assertIn("semgrep_config", decision.reason)

                allow_registry = evaluate_tool_request(
                    "workflow_verify_security",
                    {
                        "project_dir": str(project_dir),
                        "semgrep_config": "auto",
                        "run_semgrep": True,
                    },
                    policy=policy,
                )
                self.assertEqual(allow_registry.action, "allow")

    def test_c05_cli_block_level_overrides_default(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(
            ["verify-security", "REG-5", "--semgrep-block-level", "error"]
        )
        self.assertEqual(args.semgrep_block_level, ["error"])
        default_args = parser.parse_args(["verify-security", "REG-5"])
        self.assertIsNone(default_args.semgrep_block_level)

    def test_c06_percent_shaped_line_rate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "test-results.json").write_text(
                json.dumps({"summary": {"passed": 15, "failed": 0}}),
                encoding="utf-8",
            )
            (project_dir / "coverage.xml").write_text(
                '<?xml version="1.0" ?><coverage line-rate="80"></coverage>',
                encoding="utf-8",
            )
            (project_dir / "README.md").write_text("Install\nRun\nTest\n", encoding="utf-8")
            verdict = verify_artifacts(
                issue_id="REG-6",
                project_dir=project_dir,
                min_tests=15,
                min_coverage=80.0,
            )
            self.assertEqual(verdict.status, "fail")
            cov = next(c for c in verdict.checks if c.name == "coverage.xml")
            self.assertEqual(cov.status, "fail")
            self.assertIn("out of range", cov.message)


if __name__ == "__main__":
    unittest.main()
