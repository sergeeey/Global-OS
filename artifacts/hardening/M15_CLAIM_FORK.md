# M1.5 claim fork — durability harness vs cognitive real workload

**Status:** DECISION LOCKED — **Variant B**  
**Date:** 2026-09-25  
**Freeze under discussion:** `5d15600` (durability-capable; **not** cognitive-real-workload proof)

## What `5d15600` actually runs

Embedded `research_program.py` missions are **Small deterministic research mission**s:

```text
sum(1..20) == 210 and even
null probe retained
post-fault continue (same trivial class)
```

Program contract scenario lists `"research missions (deterministic)"`.  
Reframe in code: *exercise durable research loop under faults, **not prove new science***.

So the honest exam question on `5d15600` is:

```text
Hold research-runtime state for ≥48h wall,
survive injected faults,
preserve Goal / Epistemic / Authority integrity,
retain nulls, invalidate stale evidence,
recover after process kill,
finish with an auditable trail.
```

It is **not**:

```text
Do real substantive research on an external paper/dataset/open problem
for two days with new evidence, rejected hypotheses, and changing decisions.
```

Docs that said “real workload” without this distinction were **overclaiming relative to exam code**.

## Fork

| | **A — keep `5d15600`** | **B — new freeze (CHOSEN)** |
|--|------------------------|-----------------------------|
| Workload | Deterministic durability harness | Locked **external** research object + progressive probes |
| 48h claim if PASS | Narrow: *48h persistent research-**runtime** integrity under faults* | Broader (still scoped): *48h cognitive research workload with integrity under faults* |
| Preflight now | Valid Windows/fault/env evidence | Same — **do not cancel** running 96m if in progress |
| Literal 48h on `5d15600` | Allowed **only** for narrow A claim | **Forbidden** as proof of cognitive-real claim |
| Cost | Faster | New harness → tests → freeze SHA → Windows re-smoke/preflight → 48h |

## Decision

```text
Variant B
→ implement LH-COGNITIVE-v1 (eval harness; ADR-0009 OK)
→ acceptance + adversarial tests
→ new freeze SHA (not patch 5d15600)
→ Windows smoke + wall preflight on NEW SHA
→ literal ≥48h
→ independent audit within protocol scope
```

`5d15600` durability preflight (if completed) is retained as **ENV / integrity mechanics evidence**, not as M1.5 cognitive PASS.

## Operator rule (immediate)

```text
IF 96m preflight on 5d15600 is running → let it finish; label DURABILITY_ENV
DO NOT start wall_48h on 5d15600 for the cognitive-real M1.5 claim
AFTER LH-COGNITIVE freeze → new exam path
```

## Narrow A claim (only if someone insists on finishing 5d15600 48h)

> On frozen `5d15600`, within protocol scope, Global OS did/did not demonstrate
> **48h persistent research-runtime integrity under injected faults**
> (deterministic internal missions). This does **not** demonstrate 48h on a
> substantive external research object.
