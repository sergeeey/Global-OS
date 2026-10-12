# Goal Contract — PILOT3-IND-ENG-v1

**Status:** `PREREG_DRAFT`  
**Date (UTC):** 2026-10-12  
**Mode:** PILOT_USAGE — independent engineering validation  
**Depends on:** Pilot 2 TERMINAL (`PARTIAL_SUPPORT_PROCESS_ONLY`); PhaseBreak effect RECONCILED  
**ADR gate:** ADR-0009 — bugfix / eval harness / evidence / honesty only (no new T0/T1)

## Goal

```text
На одинаковом pinned engineering snapshot, с раздельными исполнителями
(или изолированными сессиями), одинаковым information set и заранее
зафиксированным бюджетом, измерить независимо:

  (EPI) снижает ли Global OS долю неподтверждённых findings / ложных claims;
  (ENG) увеличивает ли число подтверждённых существенных дефектов и
        корректных исправлений;
  (EFF) снижает ли human-review effort при сопоставимом качестве;

и attribution: выигрыш даёт полная инфраструктура Global OS
или качественная инженерная дисциплина (ablation), реализуемая проще.
```

## Hypotheses (primary — all three pre-registered)

```text
H-PILOT3-EPI
  Independent GOS arm produces fewer unsupported findings and false claims
  than independent strong-single-agent baseline (Arm A), at comparable coverage.

H-PILOT3-ENG
  Independent GOS arm produces more confirmed material defects and
  correct regression-safe fixes than Arm A.

H-PILOT3-EFF
  Independent GOS arm requires less human-review effort for comparable
  quality (confirmed findings + fix correctness) than Arm A.
```

## Attribution question (ablation)

```text
H-PILOT3-ATTR
  If Arm C (strong agent + checklist + structured ledger + mandatory repro,
  without full GOS runtime) matches Arm B on EPI/ENG/EFF, then incremental
  value of full Global OS infrastructure is NOT_SHOWN for this product shape;
  value is attributable to process discipline alone.
```

## Arms (summary)

| Arm | Stack | Isolation |
|-----|--------|-----------|
| **A** | Strong single agent, normal coding workflow | Separate executor/session |
| **B** | Full Global OS process on same pin | Separate executor/session |
| **C** | Ablation: checklist + ledger + mandatory repro; **no** Epistemic Kernel / OrgCompiler / Authority / Durable runtime | Separate executor/session |
| **E** | Blind evaluator — scores packs only; no arm chat memory | Separate from A/B/C |

## Information set (binding)

```text
same repository SHA
same initial task framing document
same network policy
same secrets (none beyond clone)
same tool allowlist
same wall + token budget caps
no cross-arm leakage of findings until after blind score seal
```

## Non-goals

- No M2 / org-superiority axiom
- No new T0/T1 architecture during pilot
- No weakening Arm A or Arm C to flatter B
- No post-hoc primary metric swap
- No PRODUCTION_PROVEN from this pilot alone
- No autonomous external merge (Proposal ≠ Effect; human gate)

## Success of the pilot

Honest terminal for EPI / ENG / EFF / ATTR with sealed blind scores.  
`REJECTED` / `TIE` / `INCONCLUSIVE` / `NOT_SHOWN` are valid outcomes.
