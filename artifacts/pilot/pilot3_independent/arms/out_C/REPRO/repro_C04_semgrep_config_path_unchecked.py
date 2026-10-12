#!/usr/bin/env python3
"""C04: semgrep_config path not in PATH_ARGUMENT_NAMES.

MCP/policy does not constrain semgrep_config even when it is a filesystem path.
If run_semgrep=True, scanner may be pointed at arbitrary config paths outside roots.

This repro shows policy allow for an outside-root config path (ToolCallSuccess of
policy check). Full WorldSuccess (semgrep actually reading the file) is NOT claimed
without a local semgrep binary — sealed as policy-surface defect only.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.tool_policy import ToolPolicy, evaluate_tool_request, PATH_ARGUMENT_NAMES


def main() -> int:
    print("PATH_ARGUMENT_NAMES=", sorted(PATH_ARGUMENT_NAMES))
    assert "semgrep_config" not in PATH_ARGUMENT_NAMES

    with tempfile.TemporaryDirectory() as allowed_tmp:
        with tempfile.TemporaryDirectory() as denied_tmp:
            policy = ToolPolicy(allowed_roots=(Path(allowed_tmp),))
            outside_config = Path(denied_tmp) / "evil.yml"
            outside_config.write_text("rules: []\n", encoding="utf-8")
            project_dir = Path(allowed_tmp) / "project"
            project_dir.mkdir()

            decision = evaluate_tool_request(
                "workflow_verify_security",
                {
                    "project_dir": str(project_dir),
                    "semgrep_config": str(outside_config),
                    "run_semgrep": True,
                },
                policy=policy,
            )
            print("action=", decision.action)
            print("reason=", decision.reason)
            print("checked_paths=", decision.checked_paths)

            if decision.action == "allow" and str(outside_config.resolve()) not in "".join(
                decision.checked_paths
            ):
                print("CONFIRMED: outside semgrep_config path not policy-checked")
                return 0
            print("NOT CONFIRMED")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
