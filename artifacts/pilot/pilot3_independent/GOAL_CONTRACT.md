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

и attribution: выигрыш даёт полный GOS runtime (Arm C)
или качественная инженерная дисциплина без GOS (Arm B).
Ключевое сравнение: C vs B (не только C vs A).
```

## Hypotheses (primary — all three pre-registered)

```text
H-PILOT3-EPI
  Independent GOS arm (C) produces fewer unsupported findings and false claims
  than independent strong-single-agent baseline (A), at comparable coverage.

H-PILOT3-ENG
  Independent GOS arm (C) produces more confirmed material defects and
  correct regression-safe fixes than Arm A.

H-PILOT3-EFF
  Independent GOS arm (C) requires less human-review effort for comparable
  quality (confirmed findings + fix correctness) than Arm A.
```

## Attribution (decisive)

```text
H-PILOT3-ATTR
  Key comparison is C vs B.
  If C beats A but not B on EPI/ENG/EFF → win may be process discipline,
    not GOS architecture (ATTR = PROCESS_DISCIPLINE_SUFFICES / GOS incremental NOT_SHOWN).
  If C beats B at comparable cost without correctness loss → first strong evidence
    of standalone GOS runtime value (ATTR = GOS_INCREMENTAL_SUPPORTED).
```

## Arms (binding labels)

| Arm | Stack | Isolation |
|-----|--------|-----------|
| **A** | Strong single agent — ordinary full engineering audit | Separate executor/session |
| **B** | Disciplined single agent — checklist + ledger + sealed repro; **no** full GOS runtime | Separate executor/session |
| **C** | Global OS — full GOS protocol and runtime on same pin | Separate executor/session |
| **D** | Independent blind evaluator — scores packs without knowing origin | Separate from A/B/C |

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

- No M2 / org-superiority axiom / agent-hierarchy scaling
- No new T0/T1 architecture during pilot
- No weakening Arm A or Arm B to flatter C
- No post-hoc primary metric swap
- No PRODUCTION_PROVEN from this pilot alone
- No autonomous external merge (Proposal ≠ Effect; human gate)
- No maturity promotion from pilots alone

## Success of the pilot

Honest terminal for EPI / ENG / EFF / ATTR with sealed blind scores from D.  
`REJECTED` / `TIE` / `INCONCLUSIVE` / `NOT_SHOWN` are valid outcomes.
