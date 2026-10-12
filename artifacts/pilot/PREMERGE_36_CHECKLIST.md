# Pre-merge checklist — PR #36 @ `bbd30c5`

**Operator strategy:** single integration merge via #36; #32–#35 superseded, not parallel deliveries.  
**Checked at:** 2026-10-12 (agent verification on tip `bbd30c53bd33478dc4610ad206ebfdd9f515e1a2`)  
**Human merge still required.**

## Four final conditions

| # | Condition | Result |
|---|-----------|--------|
| 1 | CI green **on `bbd30c5`** (not only older commits) | **PASS** — both `schemas-and-tests` success on head `bbd30c5` ([PR checks](https://github.com/sergeeey/Global-OS/pull/36)) |
| 2 | Diff reviewed: stack once + no unwanted side deliveries | **PASS with notes** — see below |
| 3 | Authority + runtime regressions on integrated tip | **PASS** — 53 targeted tests green |
| 4 | Challenge blocked; no auto-exec on merge | **PASS** — `execution_status=NOT_STARTED`; gate fail-closed; no workflow hooks |

## Diff notes (condition 2)

Expected composition (one stack, not duplicated parallel PR merges as separate products):

- merge commits: #32 → #33 → #34 → #35, then P1 + operator docs
- ~62 files, +2933/−155 vs `main` @ `2f73107`
- zero deleted files

Incidental / honesty-only paths (acceptable, not architecture expansion):

- `artifacts/safe_autonomy_t1/T3/MEASUREMENT_DEFECT_AB_SCRIPT.md` + limited `T3_DECISION.md` honesty
- `artifacts/hardening/dogfood_fm/Y18-2-effect-discrepancy/execute_mission.py` — tiny touch from stack (not Challenge exec)

No new T0/T1 kernels; no Challenge arm runners started; no ATTR/M2/PRODUCTION_PROVEN softening.

## Regression evidence (condition 3)

```text
pytest: test_auth_audit_p0, test_authority, test_m14_trust_boundary,
        test_t3_model_sensitivity, test_challenge_ga_*, test_cognitive_organ_contracts,
        test_pack_sealed_integrity, test_borrow_grounding_sop_research,
        test_durable_recovery
→ 53 passed
```

## Challenge gate (condition 4)

- `LOCK.json`: `PREREG_LOCKED` · `execution_status=NOT_STARTED`
- `forbidden` includes `execute_before_human_request`
- `assert_challenge_exec_authorized()` / `prepare_challenge_exec()` raise without human token
- organ fixture loop: `challenge_win_claimed=False`, `world_effects=False`, naive `win=False`
- `.github` workflows: no Challenge exec hooks

## After human merge (not done here)

1. Record actual `main` SHA  
2. Confirm CI on that SHA  
3. Short canon-sync to delivered tip  
4. Challenge **prep** only — no exec  

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` · `CHALLENGE_EXEC=NOT_STARTED`

## Non-claims

Merge #36 ≠ Autonomous Goal Achiever demonstrated.  
Merge #36 ≠ scientific ATTR/M2 revision.  
Only Challenge terminal evidence can answer the mission question.
