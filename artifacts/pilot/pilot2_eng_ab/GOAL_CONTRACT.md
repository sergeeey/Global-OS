# Goal Contract — PILOT2-ENG-AB-v1

**Status:** `TARGET_LOCKED` (provider/budget pins still TBD before arms)  
**Date (UTC):** 2026-10-12  
**Mode:** PILOT_USAGE — engineering A/B (not M-EXT6)  
**Depends on:** main @ `4507051` (#21); PhaseBreak effect reconciled (`0161463`)  
**Target:** `sergeeey/mcp-bouncer` @ `45af092` — see `LOCK.json`

## Goal

```text
На одном pinned engineering repository snapshot измерить,
даёт ли Global OS больше verified useful engineering work
на единицу cost/human attention, чем сильный single-agent baseline.
```

Independent value: defects found, fixes, regressions — полезны владельцу репо даже если GOS не выигрывает.

## Hypothesis (primary)

```text
H-PILOT2-001
Given the same repository snapshot,
same task contract,
same model family/provider,
same tool access,
and comparable compute budget,
Global OS produces higher verified useful engineering work
per unit of cost/human attention
than a strong single-agent baseline.
```

## Task framing (same for A and B)

> Determine production readiness of **mcp-bouncer**: find material
> correctness/security defects in the 8 attack-class prompt-injection filter,
> reproduce confirmable bypasses **or** false-positive breakage of legitimate
> MCP/JSON-RPC traffic, and propose minimal regression-safe fixes with
> failing-then-passing tests.

Not: “find as many bugs as possible.”  
Not: silently tighten filters until all tests pass while breaking MCP payloads.

## Arms

| Arm | Stack |
|-----|--------|
| **A** | Strong single agent: repo + task + tools + generous context + normal coding workflow. No Epistemic Kernel / OrgCompiler / verification branches. |
| **B** | Global OS on same snapshot/goal/model/tools/budgets |

## Information set (binding)

```text
same commit
same initial docs
same network policy
same secrets
same tools
same external sources
```

Extra research by B is allowed only via the shared tool policy and counts toward B’s cost.

## Non-goals

- No new T0/T1 architecture during the pilot
- No weakening baseline to make GOS look good
- No post-hoc metric fishing after unseal
- No Immune*/ScienceKernel
- No claim PRODUCTION_PROVEN from a single pilot

## Success of the pilot

Honest terminal with A/B ledger. Win conditions are ordered (see `PREREG.md`).
`REJECT` / `TIE` / `INCONCLUSIVE` are valid scientific outcomes.
