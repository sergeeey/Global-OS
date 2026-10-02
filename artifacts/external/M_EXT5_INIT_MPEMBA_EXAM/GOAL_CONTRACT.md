# M-EXT5 — Goal Contract

**Status:** `GOAL_LOCKED`  
**Exam id:** `M-EXT5-INIT-MPEMBA`  
**Protocol:** `M-EXT5-INIT-MPEMBA-v1`  
**After:** M-EXT4 TERMINAL + POST_HOC_AUDIT

## Goal (external scientific value)

Empirically test whether an **initialization-induced** Mpemba-like crossing exists
under identical subsequent SGD dynamics — and, separately, whether Fisher /
information geometry explains it.

This is **not** a rewrite of M-EXT4. M-EXT4 remains immutable historical triage.

## Two hypotheses (orthogonal terminals)

### H_EFFECT

> Under identical subsequent optimizer / data / noise dynamics, can two networks
> that differ only in initial state show a reproducible Mpemba-like crossing:
> at t=0 the “hot” state is farther from a pre-defined target regime than “cold”,
> yet reaches that target earlier?

### H_FISHER

> If such crossing exists, is it explained by Fisher / information-geometry
> mechanism — or by simpler alternatives?

Allowed pattern: `H_EFFECT SUPPORTED` and `H_FISHER REJECTED` (and other combinations).

## Terminal vocabulary (per hypothesis)

`SUPPORTED_WITHIN_SCOPE` | `REJECTED` | `INCONCLUSIVE`

Mission-level may also record protocol blockers, but must not merge the two questions.

## Hard sequence

```text
mechanical correctness gate (all PASS)
  → exploratory pilot (separate seeds; not confirmatory)
  → final prereg (endpoints + stats locked)
  → freeze code SHA + seal holdout
  → confirmatory run
  → independent verification
  → dual terminal
```

## Forbidden

- Rewrite M-EXT4 decision / prereg / seal  
- Use M-EXT4 `P≈0.6` or broken `14/20` rule as M-EXT5 primary  
- Treat crossing as automatic Fisher proof  
- GOS architecture edits for optics  
- Human content-coaching before terminal (exam integrity if used as exam)  
- Collect confirmatory data before mechanical gate is green  

## Budget envelope

| Resource | Cap |
|----------|-----|
| Wall investigation | **40 hours** |
| Confirmatory reseal after unseal | **0** |
| Post-hoc primary endpoint change after unseal | **0** |
| GOS architecture edits | **0** |
