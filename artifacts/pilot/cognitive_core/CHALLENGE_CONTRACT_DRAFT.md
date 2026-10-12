# CHALLENGE-GA-v1 — Open Goal-Achievement Challenge (DRAFT → superseded)

**Status:** superseded by **`PREREG_LOCKED`** pack  
**Locked pack:** `artifacts/pilot/challenge_ga/` (`LOCK.json`, `CHALLENGE_GA_CONTRACT.md`)  
**Execution:** still **NOT_STARTED** until human requests a run  

**Fidelity target:** isolated arms, sealed budget, blind or independent score  
**Substrate:** MINIMAL-STACK DEFAULT (G1+G2+G3); Gfull OPT-IN if long horizon requires it

## Intent class (example — pin concrete target at lock)

> Given project X: run a full performance audit, find bottlenecks, write benchmarks,
> optimize the critical path by a sealed % **without breaking interfaces**, and deliver
> a reproducible report with before/after measurements.

This is **not** “fix one known bug in a known file.”

## Why this shape

| Micro audit / one-step fix | Open Challenge |
|----------------------------|----------------|
| Discipline often suffices (Pilot 3 ATTR) | Needs strategy, pivots, tool/model choice |
| Short horizon | Multi-phase / multi-day possible |
| Reliability dominates score | Intelligence + Execution + Reliability jointly scored |

## Hypotheses (draft)

| Id | Claim |
|----|--------|
| H-GA-EPI | Goal Achiever retains negatives, no silent goal drift, evidence-tiered claims |
| H-GA-ENG | Produces measurable world improvement vs sealed baseline (e.g. bench delta) under interface invariants |
| H-GA-EFF | Human intervention / cost not worse than strong single agent beyond tolerance for comparable ENG |
| H-GA-ATTR | vs strong single agent **with same discipline checklist** — only scored if fidelity holds |

ATTR here is **goal-achievement ATTR**, not a silent reopen of Pilot 3 Paperclip ATTR.
Pilot 3 ATTR on audit EPI/ENG remains NOT_SHOWN until a new protocol explicitly supersedes it.

## Arms (draft)

| Arm | Stack |
|-----|--------|
| A | Strong single agent, same tools/budget, minimal process |
| B | Strong single + Pilot-3-style discipline checklist/ledger |
| C | Global OS Goal Achiever = MINIMAL-STACK substrate + Cognitive Core organs |

Decisive comparison remains **C vs B** when claiming architecture-beyond-discipline.

## Terminal goal criterion (binding at lock)

Challenge **succeeds only** if the sealed **terminal Goal success_criteria** are met
with required evidence (e.g. before/after benches + interface freeze green).

```text
WIN  = terminal Goal criteria satisfied + evidence tier met
LOSE = budget/stop hit without terminal criteria
```

Correct intermediate plans, ledger rows, pivots, or partial fixes **do not** count as WIN.
H-GA-ENG is scored on terminal world result, not on process aesthetics.

## Stop conditions (binding at lock)

| Condition | Result |
|-----------|--------|
| Terminal success_criteria met | STOP_SUCCESS |
| Wall / token / USD budget exhausted | STOP_BUDGET |
| Forbidden outcome attempted or observed | STOP_FORBIDDEN |
| Pivot attempt_budget exhausted without path | STOP_NO_STRATEGY |
| Human escalate unresolved at cap | STOP_ESCALATION |
| Fidelity break (arm contamination, pin drift) | INCONCLUSIVE |

## Lock gate (must complete before exec)

- [ ] Concrete repo + SHA + interface freeze
- [ ] Numeric success criteria (e.g. critical-path latency/throughput Δ, benches green)
- [ ] Forbidden outcomes (API break, unauthorized push, budget overrun)
- [ ] Provider/model/tool pins + wall/token caps
- [ ] Arm isolation + scoring rubric sealed
- [ ] Terminal goal criterion + stop conditions filled with concrete thresholds
- [ ] Organ contracts CONTRACTS_LOCKED (`artifacts/pilot/cognitive_core/organs/`)
- [ ] ADR-0009 check: no new T0/T1; organs behind existing kernels/gateways

## Non-claims until locked+executed

```text
≠ Cognitive Core complete
≠ Intelligence advantage shown
≠ M2 reopened
≠ PRODUCTION_PROVEN
≠ Pilot 3 ATTR overturned by draft text
≠ WIN from intermediate plans alone
```
