# Pilot 3 Arm D — Blind EVAL NOTES

**Evaluator:** pilot3-arm-D  
**Pin:** `47c232b` @ `/tmp/pilot/p3-arm-D` (`tools/workflow-controller`)  
**Baseline smoke:** `python3 -m pytest -q` → **54 passed** (not treated as readiness)  
**Unblind:** not performed (BLIND_MAP / other arms / PROTOCOL_A–C unread)

## Method

1. Retarget pack REPRO scripts to the sealed pin (hardcoded arm checkout paths rewritten locally only).
2. Confirm each asserted defect on **unpatched** tree (individual repros exit CONFIRMED and/or regression tests fail).
3. Apply pack patches (P1/P2) or reconstruct from FIXES.md (P3 — no patch file) on isolated copies; require fail→pass on pack probes and green in-tree smoke where claimed.
4. Score contested design claims against existing acceptance tests and README contracts.

## Pack P1

| ID | Score | Fix |
|----|-------|-----|
| C01 | CONFIRMED | CORRECT |
| C02 | CONFIRMED | CORRECT |
| C03 | CONFIRMED | CORRECT |
| C04 | CONFIRMED | CORRECT |
| C05 | CONFIRMED | CORRECT |
| C06 | CONFIRMED | CORRECT |
| C07 | UNSUPPORTED | — |
| C08 | UNSUPPORTED | — |

Post-fix: pack regressions 6/6 green; with regression module installed → **60 passed**. Individual C01–C06 repros flip to NOT CONFIRMED after patch.

## Pack P2

| ID | Score | Fix |
|----|-------|-----|
| F1 | CONFIRMED | CORRECT |
| F2 | CONFIRMED | CORRECT |
| F3 | CONFIRMED | CORRECT |
| F4 | UNSUPPORTED | INCORRECT |
| F5 | CONFIRMED | CORRECT |

Post-fix: pack regressions 5/5 green; in-tree suite **55 passed** (adds one policy unit test).  
F4 observation (sync→`done`) is real, but package tests lock done-on-pass; `in_progress`+`pass`→reporter is a separate mode. Patch that remaps pass→`in_progress` and rewrites those tests is a design change, not a defect fix.

Patch also appends local run residue into `events.jsonl` fixture; incidental and not part of the scored fix logic.

## Pack P3

| ID | Score | Fix |
|----|-------|-----|
| B-01 | CONFIRMED | CORRECT |
| B-02 | CONFIRMED | CORRECT |
| B-03 | CONFIRMED | CORRECT |
| B-04 | CONFIRMED | CORRECT |
| B-05 | CONFIRMED | CORRECT |
| R-01 | UNSUPPORTED | — |
| R-02 | NOT_REPRODUCED | — |
| R-03 | UNSUPPORTED | — |
| R-04 | NOT_REPRODUCED | — |
| R-05 | CONFIRMED | — |

Pre-fix: `test_confirmed_defects.py` → **7 failed**.  
Post-fix (FIXES.md reconstructed): **7 passed**; smoke **54 passed**.  
B-02 requires issue-relative path resolve before nested `evaluate_tool_request` (naive cwd resolve breaks fixture relatives); FIXES.md says “resolve” — scored CORRECT under that reading.  
R-05: pack retained as NOT_REPRODUCED; evaluator reproduced with mocked scanner exit codes → **CONFIRMED**.

## Aggregate

- Findings: confirmed **16**, not_reproduced **2**, unsupported **5**, duplicate **0**
- Fixes: correct **15**, incorrect **1** (P2 F4), untested **0**

## Epistemic notes

- ToolCallSuccess ≠ WorldSuccess noted on path-policy allows that still write/read outside intended containment.
- Local patch verification ≠ upstream merge effect; no external Paperclip PR/push performed.
- Overlapping defect themes appear across packs (event-log artifact fail, `output_file` policy, empty allowlist); each pack scored independently (no DUPLICATE marks).
