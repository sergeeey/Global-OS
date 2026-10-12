#!/usr/bin/env python3
"""C02: MCP sync_issue_state ignores output_file in path policy.

PATH_ARGUMENT_NAMES omits output_file. Policy checks issue_file/event_log but
allows writing synced issue JSON outside allowed_roots.

Expected: output_file outside allowed_roots → policy block, no write.
Observed: policy allow + write succeeds outside roots.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.mcp_tools import WorkflowToolService
from workflow_controller.tool_policy import ToolPolicy, evaluate_tool_request

ISSUE = ROOT / "tests" / "fixtures" / "issues" / "clean-issue.json"


def main() -> int:
    with tempfile.TemporaryDirectory() as allowed_tmp:
        with tempfile.TemporaryDirectory() as denied_tmp:
            allowed = Path(allowed_tmp)
            denied = Path(denied_tmp)
            outside_output = denied / "exfiltrated-issue.json"
            # issue_file lives under repo cwd — include cwd so issue_file is allowed
            policy = ToolPolicy(allowed_roots=(Path.cwd(), allowed))

            decision = evaluate_tool_request(
                "workflow_sync_issue_state",
                {
                    "issue_file": str(ISSUE),
                    "output_file": str(outside_output),
                    "event_log": str(allowed / "events.jsonl"),
                },
                policy=policy,
            )
            print("evaluate_tool_request.action=", decision.action)
            print("evaluate_tool_request.reason=", decision.reason)

            service = WorkflowToolService(policy=policy)
            response = service.sync_issue_state(
                issue_file=str(ISSUE),
                output_file=str(outside_output),
                event_log=str(allowed / "events.jsonl"),
            )
            wrote = outside_output.is_file()
            print("mcp.status_or_policy=", response.get("status") or response.get("policy", {}).get("action"))
            print("wrote_outside=", wrote)
            if wrote:
                payload = json.loads(outside_output.read_text(encoding="utf-8"))
                print("written_issue_id=", payload.get("issue_id"))

            if decision.action == "allow" and wrote:
                print("CONFIRMED: output_file outside allowed_roots not blocked")
                return 0
            print("NOT CONFIRMED")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
