# CHALLENGE-GA-v1 — Open Goal-Achievement Challenge

**Status:** `PREREG_LOCKED` — **locked for protocol; not executed**  
**Fidelity target:** isolated arms, sealed budget, independent or blind score  
**Substrate:** MINIMAL-STACK DEFAULT (G1+G2+G3); Gfull OPT-IN if long horizon requires it  
**Organs:** CONTRACTS_LOCKED (`artifacts/pilot/cognitive_core/organs/`)

## Intent

Measure whether Global OS as an **Autonomous Goal Achiever** can reach a sealed
**terminal Goal** (optimize fixture under invariants) better than a strong agent
with the same process discipline — not whether it can fill a ledger.

## Target

See `TARGET.md` — sealed in-repo fixture (checksum + ops budget).  
This is **not** “fix one known bug in a known file.”

## Hypotheses

| Id | Claim |
|----|--------|
| H-GA-EPI | Goal Achiever retains negatives, no silent goal drift, evidence-tiered claims |
| H-GA-ENG | Terminal Goal criteria met (checksum + ops budget) under interface freeze |
| H-GA-EFF | Human intervention / cost not worse than strong single agent beyond tolerance for comparable ENG |
| H-GA-ATTR | vs strong single agent **with same discipline checklist** — only scored if fidelity holds |

ATTR here is **goal-achievement ATTR**, not a silent reopen of Pilot 3 Paperclip ATTR.  
Pilot 3 ATTR on audit EPI/ENG remains **NOT_SHOWN**.

## Arms

| Arm | Stack |
|-----|--------|
| A | Strong single agent, same tools/budget, minimal process |
| B | Strong single + Pilot-3-style discipline checklist/ledger |
| C | Global OS Goal Achiever = MINIMAL-STACK + Cognitive Core organs |

Decisive comparison: **C vs B**.

## Terminal goal criterion (binding)

```text
WIN  = sealed checksum + ops ≤ budget + interface freeze + property suite
LOSE = budget/stop without terminal criteria
```

Correct intermediate plans ≠ WIN. See `SCORE_RUBRIC.md`.

## Stop conditions (binding)

| Condition | Result |
|-----------|--------|
| Terminal success_criteria met | STOP_SUCCESS |
| Wall / token / USD budget exhausted | STOP_BUDGET |
| Forbidden outcome attempted or observed | STOP_FORBIDDEN |
| Pivot attempt_budget exhausted without path | STOP_NO_STRATEGY |
| Human escalate unresolved at cap | STOP_ESCALATION |
| Fidelity break (arm contamination, pin drift) | INCONCLUSIVE |

## Budgets (sealed)

| Cap | Value |
|-----|-------|
| Wall clock | 4 h / arm |
| Tokens | 2_000_000 / arm |
| USD | 5.00 / arm (if live provider) |
| Pivot attempts | 8 / arm |
| Human escalations | 2 / arm |

## Lock gate checklist

- [x] Concrete target + sealed metrics (`TARGET.md`)
- [x] Numeric success criteria (checksum `7674672`, ops `≤ 80000`)
- [x] Forbidden outcomes
- [x] Provider/model/tool pins + wall/token caps (`LOCK.json`)
- [x] Arm isolation + scoring rubric sealed (`SCORE_RUBRIC.md`)
- [x] Terminal goal criterion + stop conditions
- [x] Organ contracts CONTRACTS_LOCKED
- [x] ADR-0009: no new T0/T1 surfaces; eval/contract only
- [ ] **Execution** — forbidden until human requests run after merge

## Non-claims (binding until executed + scored)

```text
≠ Cognitive Core complete
≠ Intelligence advantage shown
≠ M2 reopened
≠ PRODUCTION_PROVEN
≠ Pilot 3 ATTR overturned
≠ WIN from intermediate plans alone
≠ T3 historical KEEP as Achiever proof
```
