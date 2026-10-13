# ADR-0014 — Goal-conditioned continual improvement (Mission Learning Loop)

## Status

Accepted — 2026-10-13 (design + eval harness v0; Continual SI still NOT_MEASURED)

## Context

Research (DGM, AlphaEvolve, ADAS/AHE, POET-class coevolution) shows useful
patterns: version archives, objective evaluators, harness evolution, and
failure-driven curricula. Global OS must not treat RSI as a separate product.

Primary mission remains:

> Human sets Goal, constraints, and authority. Global OS plans, tools, executes,
> pivots, and delivers a **verified** result.

Self-improvement must serve that mission. ADR-0009 still bars unplanned T0/T1
kernels. GOS-I20: gated self-improvement only.

## Decision

### Generations (honesty)

| Gen | Name | Status |
|-----|------|--------|
| 1 | Autonomous Goal Achiever | Current priority — not yet PRODUCTION_PROVEN |
| 2 | Continually Improving Achiever | Starts as Mission Learning Loop v0 (eval) |
| 3 | Co-Evolving Goal Intelligence | Research horizon — not started |

### Contours

```text
A — Goal Achievement     Goal → plan → tools → verify → result
B — Experience Evolution Experience → candidates → tournament → archive
C — Challenge Evolution  Weaknesses → new stress tasks → transfer check
                         (never trains on sealed Challenge-GA holdout)
```

Independent admission boundary (immutable by the improving agent):

- Independent scorer · Authority Kernel · Sandbox · Human promotion · Rollback
  of **candidates** (not unconditional `git revert` of external world effects)

### Mission Learning Loop v0 (in scope now)

T2/eval harness only:

1. Archive one mission record (goal, plan, failures, costs, verified outcome).
2. Diagnose one confirmed `failure_class`.
3. Propose exactly two **unprivileged** workflow candidates + unchanged baseline.
4. Score all three on the same frozen public suite (independent scorer, fixed budget).
5. Archive winners, alternatives, and losses.
6. Promotion status always `REQUIRES_HUMAN` — never auto-apply to runtime.

### Forbidden now

- Self-modify Authority, success criteria, scorer, or rollback infrastructure
- Use Challenge-GA as a training suite for improvement tournaments
- Weight-level self-adaptation / SEAL-class training
- Claiming L4/L5 RSI, Continual SI measured, or competitive advantage
- Auto-promote MLLv0 winners into default Achiever runtime before Contour A
  is executable end-to-end (separate P1 track)

## Consequences

+ Clear path from Gen1 Achiever → measurable Gen2 improvement without
  architecture rewrite.
+ Improvement Candidate contract is falsifiable and promotion-gated.
− Continual SI remains NOT_MEASURED until transfer evidence exists.
− Contour C (coevolution) deferred until P1–P3 gates pass.

## Tracking

- Pack: `artifacts/pilot/mission_learning/`
- Harness: `src/global_os/evals/mission_learning/`
- Tests: `tests/test_mission_learning_loop_v0.py`
- P1 Achiever deepen: `artifacts/pilot/mission_learning/P1_ACHIEVER_GATE.md`
