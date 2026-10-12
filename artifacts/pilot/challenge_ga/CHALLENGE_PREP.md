# CHALLENGE-GA-v1 — prep checklist (no exec)

**Status:** PREP_ONLY  
**Lock:** `LOCK.json` → `execution_status=NOT_STARTED`  
**Forbidden:** run arms / claim WIN / soften ATTR / reopen M2 / bump PRODUCTION_PROVEN

This file prepares execution hygiene. It does **not** authorize Challenge.

## Terminal criteria (locked)

| Check | Source | Ready? |
|-------|--------|--------|
| Sealed checksum `process_items(list(range(400))) == 7674672` | `SCORE_RUBRIC.md` / scorer | yes — harness asserts |
| Ops budget `last_ops() <= 80000` | same | yes — naive fixture fails (160000) |
| API signature frozen | `TARGET.md` | documented |
| Intermediate plans ≠ WIN | scorer + fixture loop | yes — `challenge_win_claimed=False` |

## Gate

| Check | Mechanism |
|-------|-----------|
| Human authorization | `prepare_challenge_exec` / `HUMAN_REQUEST_CHALLENGE_GA_EXEC` or lock `AUTHORIZED` |
| Default | fail-closed `ChallengeExecForbidden` |
| Env alone | **never** sufficient |

## Budgets (from LOCK)

- wall ≤ 4h / arm · tokens ≤ 2e6 / arm · USD ≤ 5 / arm  
- pivot attempts ≤ 8 / arm · human escalations ≤ 2 / arm  

## Isolation / arms

| Item | Requirement | Prep note |
|------|-------------|-----------|
| Arms A / B / C | Isolated worktrees or equivalent; no cross-arm leakage | document at exec time |
| Decisive comparison | C vs B | locked |
| Artifact reproducibility | checksum + ops + receipts under arm id | scorer path ready; arm runner not started |
| Stop conditions | SUCCESS / BUDGET / FORBIDDEN / NO_STRATEGY / ESCALATION / INCONCLUSIVE | locked in LOCK.json |

## Organs (honesty)

| Organ | Contract | Live Achiever |
|-------|----------|---------------|
| Decomposer | LOCKED | NOT SHOWN |
| Orchestration | LOCKED | NOT SHOWN |
| Pivot | LOCKED | NOT SHOWN |
| Fixture loop (eval) | present in `evals/challenge_ga/` | ≠ Challenge WIN |

## Before human says exec

- [ ] Strategy A or B merge landed on `main`; tip SHA recorded
- [ ] Canon sync distinguishes mechanisms / fixture / Achiever
- [ ] Authority negative suite + T3 sensitivity green on combined tip
- [ ] Scorer probe on sealed naive fixture: `win=false`, checksum=7674672
- [ ] Explicit token or lock flip to AUTHORIZED
- [ ] Arm isolation plan written for this run

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` · `CHALLENGE_EXEC=NOT_STARTED`
