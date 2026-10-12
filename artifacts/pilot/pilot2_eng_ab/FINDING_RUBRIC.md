# Finding rubric — PILOT2-ENG-AB-v1

A candidate counts as a **confirmed useful finding** only if **all** hold:

```text
reproducible
+ material
+ specific
+ supported by code/runtime evidence
+ independently checked
```

## Does NOT count

| Anti-pattern | Why |
|--------------|-----|
| “race condition possible” without path | non-specific |
| Style / nits without correctness impact | not material |
| LLM confidence without evidence | not evidence |
| Duplicate of already-filed finding | no new value |
| Speculative CVE-class claim without PoC | not reproducible |

## Does count

| Example class | Minimum evidence |
|---------------|------------------|
| Correctness bug | specific path + triggering condition + observed failure + regression test (or sealed repro script) |
| Runtime crash | stack/log + minimal repro |
| Claim vs artifact mismatch | claim quote + contradicting artifact hash/path + severity |
| Broken test/CI gate | failing command + root cause note |
| Security-relevant defect | safe local PoC; no weaponized exploit publication required for score |

## Severity (pre-score)

| Level | Definition |
|-------|------------|
| Critical | data loss, auth bypass, silent wrong money/state |
| Major | wrong result in primary path, crash on common input |
| Minor | edge-path defect with clear user impact |
| Hygiene | docs/claim inconsistency only (tracked separately; not primary “useful finding” unless task asks readiness claims) |

## Independent check

Second pass by a different agent/human using only the finding pack (no chat memory).  
Must reproduce or mark `NOT_REPRODUCED` (then finding does not count for primary metric).

## Unsupported claim tally

Any arm assertion that fails the rubric above increments **unsupported claims** for that arm.
