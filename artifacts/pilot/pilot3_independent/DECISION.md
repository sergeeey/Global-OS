# DECISION — PILOT3-IND-ENG-v1

**Status:** `TERMINAL`  
**Date (UTC):** 2026-10-12  
**Target:** `sergeeey/Paperclip-AI---2026@47c232b` (`tools/workflow-controller`)  
**Fidelity:** `ISOLATED_SUBAGENT_ARMS_SAME_ORCHESTRATOR`  
**Blind map (unsealed after EVAL_SEAL):** P1→C, P2→A, P3→B  
**Evaluator:** [Pilot3 Arm D](bc-4f0e1ef9-9cf3-5785-8d86-5b4f14ecb804)

## Terminal

```text
H-PILOT3-EPI (C vs A)   = SUPPORTED
H-PILOT3-ENG (C vs A)   = SUPPORTED
H-PILOT3-EFF (C vs A)   = INCONCLUSIVE

H-PILOT3-ATTR (C vs B)  = PROCESS_DISCIPLINE_SUFFICES
GOS incremental value   = NOT_SHOWN  (at this fidelity / n)

Production readiness of target = NOT_PROVEN (defects confirmed)
PRODUCTION_PROVEN (Global OS)  = 0
M2 / org superiority           = NOT started / NOT claimed
```

## Blind scores (D)

| Pack | Arm | Confirmed | Unsupported | Not repro | Correct fixes | Incorrect fixes |
|------|-----|-----------|-------------|-----------|---------------|-----------------|
| P2 | A | 4 | 1 | 0 | 4 | 1 |
| P3 | B | 6 | 2 | 2 | 5 | 0 |
| P1 | C | 6 | 2* | 0 | 6 | 0 |

\*C’s two UNSUPPORTED rows are C07 (rejected-by-arm design dual-path) and C08 (readiness non-claim). Among **asserted defects** C is 0/6 unsupported.

## Ordered evaluation

### EPI — C vs A → SUPPORTED

C asserted six defects; D confirmed all six (unsupported_among_asserted_defects = 0).  
A asserted five; D unsupported one (F4) and marked its fix INCORRECT.

### ENG — C vs A → SUPPORTED

C: 6 confirmed + 6 correct fixes.  
A: 4 confirmed + 4 correct / 1 incorrect.  
Shared core with B/C: `output_file` path bypass, event-log artifact-fail FP, empty allowlist.

### EFF — INCONCLUSIVE

No sealed human-review minutes / intervention metering under this run.

### ATTR — C vs B → PROCESS_DISCIPLINE_SUFFICES

Decisive comparison. Confirmed counts **tied at 6**.  
B showed checklist/ledger/negative-retention value (and D even upgraded B’s R-05).  
C added unique medium findings (semgrep_config path, CLI block-level, coverage line-rate) with a full correct fix set.  
Under 15% relative tolerance, **C does not dominate B** on EPI+ENG+EFF jointly → incremental GOS runtime/process-beyond-discipline **NOT_SHOWN**.

## Independent engineering value (regardless of A/B/C win)

Material defects with sealed repro on Paperclip workflow-controller (path policy, event-log, allowlist, coverage/CLI).  
Proposal ≠ Effect respected (no autonomous Paperclip merge).

## Fidelity honesty

```text
≠ independent two-lab / distinct-provider replication
= separate subagent sessions + blind D + sealed briefs
Parent orchestrator could still bias via shared model family / repo familiarity.
```

## Implications

1. Do **not** open M2 on “organization superiority.”
2. Product-shaped value remains **evidence-backed repo auditing**; much of Pilot 3’s engineering yield is reproducible with Arm B discipline alone.
3. Next upgrades: distinct providers/executors; meter EFF; optional external fix WorldInteraction on Paperclip (human gate).

## Artifacts

- `LOCK.json` / `TASK_BRIEF.md` / `TARGET_SELECTION.md`
- `arms/out_{A,B,C}/` + `arms/out_D/EVAL_SEAL.json`
- `arms/out_D/BLIND_MAP.json` (unsealed)
- `score/SCOREBOARD.json`
- `DECISION.md` (this file)
