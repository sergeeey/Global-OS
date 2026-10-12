# Arm B REPRO

```bash
# Against unpatched tree: expect 7 failed
# Against /tmp/pilot/p3-arm-B after FIXES.md: expect 7 passed
cd /tmp/pilot/p3-arm-B/tools/workflow-controller
python3 -m pytest /workspace/artifacts/pilot/pilot3_independent/arms/out_B/REPRO/test_confirmed_defects.py -v
```

Artifacts:
- `red_before_fix.txt` — baseline failures on stock `47c232b`
- `green_after_fix.txt` — after minimal patches
- `smoke_after_fix.txt` — full package suite still 54 passed
