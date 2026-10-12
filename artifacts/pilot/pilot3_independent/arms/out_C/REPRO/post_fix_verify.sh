#!/usr/bin/env bash
# Verify Arm C patches in /tmp/pilot/p3-arm-C (local only).
set -euo pipefail
ROOT=/tmp/pilot/p3-arm-C/tools/workflow-controller
cd "$ROOT"
python3 -m pytest -q tests/test_pilot3_arm_c_regressions.py
python3 -m pytest -q
echo "post_fix_verify: OK"
