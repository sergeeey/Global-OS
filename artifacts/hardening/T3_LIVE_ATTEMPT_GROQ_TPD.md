# T3 live attempt — Groq TPD exhausted (2026-09-30)

**Status:** environment blocker (not mechanism failure)  
**Protocol:** `SAFE_AUTONOMY_T3-v1` continuation (same prereg / PACK-v3 / C2)  
**Claim:** none — live-LLM generalization **not established**

## What was proven

| Check | Result |
|-------|--------|
| `GROQ_API_KEY` in Cloud Agent env | present (`len=56`, prefix `gsk_`, no trailing WS) |
| `GET /openai/v1/models` | HTTP 200 |
| Chat completions (small) | HTTP 200 when under quota |
| `free_live_ready()` | `True` (groq only) |

## What blocked the live run

Groq free tier **tokens per day (TPD)**:

```text
Limit 200000, Used ~199861, Requested ~374
type=tokens code=rate_limit_exceeded
Retry-After ≈ 60–102s (rolling window drip)
x-ratelimit-limit-requests 1000 (day window ~13h remaining)
```

A prior long `t3_runner` attempt (~60 min) under RPM=30 burned nearly the entire TPD budget before writing SCORE_RAW (artifacts written only after both L1+L2 finish). Subsequent calls looped on 429/TPD.

## Harness response (this PR)

1. Bounded 429/503 retry (RPM-class) — **not** day-quota
2. Groq POST pacing (~2.1s) to stay under RPM≈30
3. **Fail-closed immediately** on TPD/RPD body markers (no multi-minute sleep storm)
4. T3 **live preflight** → INCONCLUSIVE `provider_quota_exhausted_live_layer` without pretending LIVE_LLM

## Operator next

1. Wait for Groq TPD rolling window to recover **or** add OpenRouter/Gemini free keys
2. Re-run: `PYTHONPATH=src python3 -m global_os.evals.trust.t3_runner`
3. Do **not** create PACK-v4 / edit C2 / promote Trust Kernel

## Explicit non-claims

- Key validity ≠ quota sufficiency
- HTTP 200 on `/models` ≠ live T3 complete
- Partial live burn ≠ KEEP/REJECT
