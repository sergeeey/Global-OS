# Finding rubric — PILOT3-IND-ENG-v1

A candidate counts as a **confirmed useful finding** only if **all** hold:

```text
reproducible
+ material
+ specific
+ supported by code/runtime evidence
+ independently checked by blind evaluator E
```

## Does NOT count

| Anti-pattern | Why |
|--------------|-----|
| “race possible” without path | non-specific |
| Style / nits without correctness impact | not material |
| Model confidence without evidence | not evidence |
| Duplicate of sealed prior finding on same SHA | no new value (disclose if rediscovery) |
| Speculative CVE without local PoC | not reproducible |
| Finding only from leaked other-arm notes | protocol break |

## Does count

| Example class | Minimum evidence |
|---------------|------------------|
| Correctness bug | path + trigger + observed failure + repro |
| Security-relevant filter bypass/FP | safe local PoC + expected class |
| Broken test/CI gate | failing command + root cause |
| Claim vs artifact mismatch | quote + contradicting artifact |

## Blind evaluation protocol

1. Arms submit packs with stable finding ids; operator strips arm labels → packs `P1/P2/P3`.
2. E scores each finding: `CONFIRMED` / `NOT_REPRODUCED` / `UNSUPPORTED` / `DUPLICATE`.
3. E scores each proposed fix: `CORRECT` / `INCORRECT` / `UNTESTED` (must run sealed tests when present).
4. Mapping P→arm unsealed only after E submits `EVAL_SEAL.json`.

## Unsupported claim tally

Any arm assertion that fails this rubric increments **unsupported claims**
for EPI scoring.
