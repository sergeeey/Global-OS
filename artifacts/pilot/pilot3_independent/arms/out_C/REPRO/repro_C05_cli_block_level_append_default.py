#!/usr/bin/env python3
"""C05: argparse append + default sticky for --semgrep-block-level.

Passing --semgrep-block-level error appends to default ["error","warning"]
instead of replacing, so CLI cannot select only {"error"}.

Expected: user-supplied levels replace or clear defaults.
Observed: default always retained under action=append.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/tmp/pilot/p3-arm-C/tools/workflow-controller")
sys.path.insert(0, str(ROOT))

from workflow_controller.cli import _build_parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args(
        [
            "verify-security",
            "REPRO-5",
            "--semgrep-block-level",
            "error",
        ]
    )
    levels = args.semgrep_block_level
    print("parsed_levels=", levels)
    if levels == ["error", "warning", "error"] or (
        "warning" in levels and levels.count("error") >= 1 and levels != ["error"]
    ):
        print("CONFIRMED: cannot override default block levels via CLI append")
        return 0
    print("NOT CONFIRMED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
