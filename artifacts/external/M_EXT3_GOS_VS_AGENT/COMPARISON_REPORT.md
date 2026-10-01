# M-EXT3 Comparison Report — GOS vs strong single agent

**Protocol:** `M-EXT3-GSA-v1`  
**Task:** [encode/httpx#3614](https://github.com/encode/httpx/issues/3614) @ `b5addb6`  
**Primary verdict:** `TIE`

## Primary

| Arm | Role | HG | Terminal |
|-----|------|----|----------|
| A | Strong single agent | 1 | `ROOT_CAUSE_CONFIRMED` |
| B | GOS assembled workflow | 1 | `ROOT_CAUSE_CONFIRMED` |

```text
HG(A)=1 ∧ HG(B)=1 → TIE
H_GSA (B primary advantage): NOT CONFIRMED
```

Both arms met all hard gates: stable repro, mechanism + disconfirming tests,
patch eliminates, regression fail-before / pass-after.

## Shared technical finding (external value)

`_enforce_trailing_slash` appended `/` to `URL.raw_path` (path **plus** query),
corrupting query values (`data=1` → `data=1/`). Fix: enforce slash on `path` only.

Upstream-ready diffs live under each arm’s `workdir/proposed_fix.diff`.

## Secondary (non-primary)

Arm B produced formal `COMPETING_EXPLANATIONS.md`, counterevidence matrix, and
`ROOT_CAUSE.md`. Arm A used minimal notes. Process richness differed; **primary
score does not award B_ADVANTAGE for docs alone** (prereg rule).

## Integrity caveats

- Same cloud-agent lineage ran A then B sequentially (recorded).
- Arm workdirs isolated; B investigation artifacts claim `read_arm_A=false`.
- Not a multi-run statistical comparison; n=1 external task.
- Universal GOS superiority: **not claimed**.

## What this exam shows

On this pinned OSS incident, under equal budgets, **both** the strong single
agent and the GOS workflow could deliver a hard-gated external engineering
result. That is useful calibration — not a win for either arm.
