# Arm D — Blind evaluator

You receive anonymized packs `P1`, `P2`, `P3` (no arm labels).

For each finding:

- `CONFIRMED` / `NOT_REPRODUCED` / `UNSUPPORTED` / `DUPLICATE`
- For each proposed fix: `CORRECT` / `INCORRECT` / `UNTESTED`

You may clone the target pin and run pytest/repro scripts.  
Do **not** try to guess which pack is GOS.  
Output: `EVAL_SEAL.json` then stop.
