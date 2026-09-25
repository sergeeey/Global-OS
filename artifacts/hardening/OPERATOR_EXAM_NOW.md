# OPERATOR_EXAM_NOW — start Windows exam on freeze `5d15600`

**No project pause required.** Only the exam SHA is frozen.

```text
Goal if closing M1.5 path:
  checkout --detach 5d15600256a7afc7839f190ed3d889b33bc3217b
  → Windows os_kill smoke
  → Windows 60–120m preflight
  → if PASS → literal ≥48h real workload
  → independent audit
  → M1.5 candidate (only then)
```

Full commands: `long_horizon_48h/WINDOWS_FROZEN_EXAM.md`

## Rules

1. Do **not** patch `5d15600` during exam.  
2. Bug on preflight ⇒ fix elsewhere ⇒ **new freeze SHA**.  
3. Linux compressed preflight / Linux os_kill already PASS — they do **not** replace Windows.  
4. Do **not** claim M1.5 from preflight alone.

## If you want more R-missions first

Work on `main`, then pick a **new** freeze after R4/R5. `5d15600` remains a historical candidate, not the exam machine.
