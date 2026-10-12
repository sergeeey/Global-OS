# MINIMAL-STACK-v1 — Product Contract

**Status:** `LOCKED`  
**Date (UTC):** 2026-10-12  
**Tip pin:** `9576311` (`main` after #29)  
**Evidence parents:**
- Pilot 3 TERMINAL — ATTR = PROCESS_DISCIPLINE_SUFFICES / GOS incremental NOT_SHOWN
- ARCH-ABLATION-MECH-v1 TERMINAL — H-ABL-G1/G2/G3/Gfull SUPPORTED at `SCRIPTED_MECHANISM_ABLATION`

## 1. Goal

Define the **default product mechanism stack** justified by sealed failure classes,
and the **claim boundary** that marketing / engineering / research must not cross.

```text
Product ≠ “full Global OS beats disciplined agent on audits”
Product = “minimal fail-closed mechanisms for specific invariant breaks”
```

## 2. Frozen parent invariants

```text
Pilot 3 ATTR (C vs B)     = PROCESS_DISCIPLINE_SUFFICES
GOS incremental (Pilot 3) = NOT_SHOWN
M2 (org superiority)      = CLOSED
PRODUCTION_PROVEN         = 0
```

Scripted ablation **does not** overturn Pilot 3 ATTR on LLM audit EPI/ENG.

## 3. Failure-class → mechanism map (binding)

| Failure class | Sealed scenario | Minimal layer that catches | Default? |
|---------------|-----------------|----------------------------|----------|
| Silent goal mutation | S1 | **G1** Goal Contract immutability | YES |
| Negative-result erasure / append-only break | S2 | **G1** EventLedger append-only | YES |
| ToolSuccess treated as WorldSuccess | S4 | **G2** EffectReceipt / reconciliation | YES |
| Privilege expansion on handoff/grant | S3 (auth) | **G3** AuthorityKernel fail-closed | YES |
| Crash mid-workflow without resume | S2 (durable) | Gfull DurableRunner | OPT-IN |
| Summary-only handoff info loss | S3 (info) | Gfull artifact-first handoff | OPT-IN |

### Default product stack

```text
DEFAULT = G1 + G2 + G3
  = immutable Goal Contract
  + append-only ledger
  + EffectReceipt / Proposal≠Effect gate
  + Authority + ToolGateway fail-closed
```

### Not default

```text
Gfull (DurableRunner + artifact handoff) = OPT-IN
  enable only when the mission’s sealed risk includes long-running crash resume
  and/or control-transfer information loss
```

Do **not** ship Gfull (or OrgCompiler / recursive topologies) as the default for
audit-style products.

## 4. Claim taxonomy (binding)

| Class | May say | Must not say |
|-------|---------|--------------|
| `VERIFIED_CURRENT_VALUE` | DEFAULT stack prevents sealed S1/S2/S4 breaks and S3 privilege expansion under scripted ablation; Pilot 2/3 show disciplined audit workflow value; mcp-bouncer external merge+CI | “GOS required for good audits”; “beats Arm B on EPI/ENG” |
| `PLAUSIBLE_POTENTIAL` | DEFAULT stack is useful infrastructure for durable evidence, effect authz, fail-closed tools | “proven product-market fit” / PRODUCTION_PROVEN |
| `NOT_SHOWN` | Incremental GOS value vs Pilot 3 Arm B discipline on LLM audit quality | Soften to “probably shown” |
| `SPECULATIVE_POTENTIAL` | Org topologies, long-horizon compounding, self-improvement | Treat as roadmap commitments |

## 5. Decision rules for builders

1. **Start from DEFAULT (G1+G2+G3).** Add Gfull pieces only with an explicit failure-class justification in the goal/mission contract.
2. **Checklist discipline (Pilot 3 Arm B)** remains valid for audit yield; do not deprecate it to flatter GOS.
3. **New architecture surfaces** still blocked by ADR-0009 until separately authorized.
4. **Reopen M2** only with a new sealed ATTR-class protocol that beats disciplined B — not via optimism or scripted-only evidence.
5. **External WorldInteraction** (e.g. Paperclip fix) is a separate human-gated track; success there ≠ ATTR overturn.

## 6. Exclusion zone

```text
E — do not do now:
  reopen M2
  soften Pilot 3 ATTR
  mark PRODUCTION_PROVEN
  invent M-EXT6 / ScienceKernel / Trust Kernel promote
  default to recursive_hierarchy / Gfull for every mission
  new T0/T1 layers “because ablation passed”
```

## 7. Success criteria (this lock)

- [x] Contract sealed with tip pin + parent invariants
- [x] Failure-class → layer map explicit
- [x] DEFAULT vs OPT-IN named
- [x] Claim taxonomy restated
- [x] Acceptance guard test exists (`tests/test_minimal_stack_contract.py`)
- [x] Roadmap / Tasktracker / honesty map point here

## 8. Next (after this lock)

Ordered options — pick explicitly; do not do all at once:

1. Implement/dogfood DEFAULT stack on a real audit mission with claim-boundary checklist (no ATTR claim).
2. Optional human: Paperclip WorldInteraction.
3. Optional new prereg: higher-fidelity field ablation (distinct providers) — only if seeking ATTR-class evidence.
