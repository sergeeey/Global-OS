#!/usr/bin/env python3
"""C03: empty allowed_tools disables allowlist (falsy tuple).

evaluate_tool_request:
  if policy.allowed_tools and tool_name not in policy.allowed_tools: block

Empty tuple is falsy → unknown tools are allowed.

Expected: empty allowlist means deny-all (or explicit block of non-listed).
Observed: ToolPolicy(allowed_tools=()) allows arbitrary tool names.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.tool_policy import ToolPolicy, evaluate_tool_request


def main() -> int:
    policy = ToolPolicy(allowed_tools=(), allowed_roots=(Path.cwd(),))
    decision = evaluate_tool_request(
        "shell_exec_anything",
        {"command": "id"},
        policy=policy,
    )
    print("action=", decision.action)
    print("reason=", decision.reason)
    print("matched_rule=", decision.matched_rule)

    if decision.action == "allow":
        print("CONFIRMED: empty allowed_tools permits unknown tool")
        return 0
    print("NOT CONFIRMED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
