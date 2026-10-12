# Arm A — Strong single-agent baseline

**Protocol:** direct engineering audit (no Epistemic ledger / OrgCompiler)  
**Target:** `mcp-bouncer@45af092`  
**Smoke:** upstream `50 passed`

## Deliverable style

Fast production-readiness pass: find bypasses, note FPs, sketch fixes.

## Findings reported (A)

| Id | Severity | Claim | Independently confirmed? |
|----|----------|-------|--------------------------|
| A1 | major | `;rm` / `\|cat` / `&& rm` bypass command_injection | **YES** (repro tests fail expecting block) |
| A2 | major | `Ignore your previous…` bypasses system_override | **YES** |
| A3 | critical | `sanitize()` then `scan()` erases ZWSP detection | **YES** |
| A4 | major | `bypass all safety` misses jailbreak | **YES** |
| A5 | major | `$(date)` false positive | **YES** |
| A6 | major | `` `sudo …` `` false positive | **YES** (matrix) |
| A7 | major | `` `bash -c id` `` bypass | **YES** (matrix) |
| A8 | minor | fullwidth/combining unicode bypass | **YES** (matrix) |
| A9 | hygiene | “~90%” claim unmeasured | asserted without sealed corpus |

## Unsupported / weak (A)

| Item | Issue |
|------|-------|
| “Not production ready” as binary | no sealed readiness rubric in A |
| Fix sketches without regression PR | proposal only |
| Did not systematically catalog LOW-only classes vs hook policy | gap |

## Process metrics (A)

| Metric | Value |
|--------|-------|
| Confirmed useful (post independent check) | 7 defect classes (A1–A7 + unicode as A8) with repro |
| False positives called out | 2–3 (incomplete vs B) |
| Unsupported claims | ≥1 (`~90%`) |
| Provenance pack | none beyond this markdown |
| Human interventions | 0 |
| Reproducible fix PRs opened on mcp-bouncer | 0 (audit-only arm) |

## Arm A self-summary

Strong single agent quickly surfaces the important regex holes and the sanitize footgun.  
Weaker on claim discipline and FP catalog completeness.
