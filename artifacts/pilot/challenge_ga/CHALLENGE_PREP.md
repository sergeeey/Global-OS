# CHALLENGE-GA-v1 — prep checklist (no exec)

**Status:** PREP_READY_FOR_AUTHORIZE (not authorized)  
**Integration SHA:** `232022c` — CI SUCCESS on `main`  
**Lock:** `LOCK.json` → `execution_status=NOT_STARTED`  
**Forbidden:** run arms / claim WIN / soften ATTR / reopen M2 / bump PRODUCTION_PROVEN

This file prepares execution hygiene. It does **not** authorize Challenge.

## Integration baseline (fixed)

| Item | Value |
|------|-------|
| Integration SHA | `232022ce9020c056552a171d390fb6ccbd9019bc` (`232022c`) |
| CI | SUCCESS — [run 38432567001](https://github.com/sergeeey/Global-OS/actions/runs/38432567001) |
| Includes | #37 MLLv0/Completion Gate · #38 Achiever loop · #39 durable/HMAC P0 |
| Canon tip after sync | `7f257bb` (docs only) |

## Terminal criteria (locked)

| Check | Source | Ready? |
|-------|--------|--------|
| Sealed checksum `process_items(list(range(400))) == 7674672` | `SCORE_RUBRIC.md` / scorer | yes — harness asserts |
| Ops budget `last_ops() <= 80000` | same | yes — naive fixture fails (160000) |
| API signature frozen | `TARGET.md` | documented |
| Intermediate plans ≠ WIN | scorer + fixture loop + Completion Gate | yes — `challenge_win_claimed=False` |

## Gate

| Check | Mechanism |
|-------|-----------|
| Human authorization | `prepare_challenge_exec` / `HUMAN_REQUEST_CHALLENGE_GA_EXEC` or lock `AUTHORIZED` |
| Default | fail-closed `ChallengeExecForbidden` |
| Env alone | **never** sufficient |
| Merge of #37–#39 | **does not** authorize exec |

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
| Decomposer | LOCKED | harness wired |
| Orchestration | LOCKED | harness wired |
| Pivot | LOCKED | harness wired |
| Completion Gate | wired to fixture | ≠ Challenge WIN |
| Achiever organ loop | on `main` @ `232022c` | IMPLEMENTED / **NOT CHALLENGED** |
| Fixture loop (eval) | `evals/challenge_ga/` | ≠ Challenge WIN |

## Before human says exec

- [x] Integration landed on `main`; tip SHA recorded (`232022c`)
- [x] CI green on integration SHA
- [x] Canon sync distinguishes mechanisms / fixture / Achiever
- [x] P0 durable/HMAC + authority bind on main
- [ ] Scorer probe re-confirmed on sealed naive fixture at exec time
- [ ] Explicit token or lock flip to AUTHORIZED
- [ ] Arm isolation plan written for this run
- [ ] Strict durable gate path env set if material arms use Gateway (`GOS_REQUIRE_DURABLE_GATE` / `GOS_DURABLE_GATE_PATH`)

## Residual (non-blocking for prep)

HMAC observation attestation binds `effect|source|method` only — not yet
`action_id` / `goal_id` / time. Documented; do not claim freshness proven.

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` · `CHALLENGE_EXEC=NOT_STARTED` · `CONTINUAL_SI=NOT_MEASURED`
