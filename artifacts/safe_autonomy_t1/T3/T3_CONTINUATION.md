# T3 CONTINUATION — same prereg, not a new sealed replication

**Status:** `AWAITING_PROVIDER_QUOTA` (keys present; Groq TPD exhausted)  
**Protocol:** `SAFE_AUTONOMY_T3-v1` (unchanged)  
**JSON:** `T3_CONTINUATION.json`

## Binding facts

```text
PACK-v3 was unsealed at SHA c6523a6.
Live execution was first blocked by missing provider credentials.
Keys later loaded (Cloud Agent GROQ_API_KEY) — /models HTTP 200.
Live run then blocked by Groq tokens-per-day (TPD≈200k exhausted).
No C2 / harness / decision-rule changes were made after unseal
beyond honesty tooling (bounded 429 retry, pacing, preflight).
Subsequent live run is a continuation of T3 under the same prereg,
not a new sealed replication.
```

## Interpretation

| Item | Status |
|------|--------|
| T2 C2 on deterministic PACK-v2 | KEEP |
| T3 generalization | INCONCLUSIVE |
| Reason (keys) | was `provider_key_unavailable_live_layer` |
| Reason (now) | `provider_quota_exhausted_live_layer` (Groq TPD) |
| C2 | unchanged (pin `e6dfd08`) |
| Trust Kernel | not promoted |
| live-LLM claim | not established |
| PACK-v4 | **not created** — finish T3 continuation first |

Evidence: `artifacts/hardening/T3_LIVE_ATTEMPT_GROQ_TPD.md`

## Post-unseal integrity attestation

| Artifact | SHA256 (content) | Post-unseal edits |
|----------|------------------|-------------------|
| `recovery_router.py` | `09e00e4f67f8b8c05eab5e0f212b39fb5244375ad3e20b699126a1ce2e652597` | none after `c6523a6` |
| `SELECTIVE_BOUNDED_RECOVERY_V1.json` | `4df0056fc101b69e07f9623d26b76433c1c0a5761149b9037b894688be74636b` | none after unseal |
| `T3_PREREG.json` | `e3f9504d9321f98c63358c13485c91f1478af22d70cc824c2a8c9cfaeb5ba19a` | none after unseal |
| T3 experiment SHA freeze | `c6523a6bb58484a018ae4638949ad4aa085b4095` | write-once |

If anyone had changed C2 / thresholds / routing after viewing PACK-v3, this pack would lose clean-holdout status and a new sealed pack would be required. **That did not happen.**

## Operator continuation steps

```text
1. Wait for Groq TPD recovery and/or load OPENROUTER_API_KEY / GEMINI_API_KEY
2. Do not change C2 / SELECTIVE_BOUNDED_RECOVERY-v1
3. Do not change T3 prereg / thresholds / PACK-v3
4. Run:
   PYTHONPATH=src python3 -m global_os.evals.trust.t3_runner
5. Expect preflight fail-closed on day-quota (INCONCLUSIVE) rather than hour-long 429 sleep
6. Record KEEP / REJECT / INCONCLUSIVE
```

## Verdict policy (unchanged)

| Verdict | Meaning |
|---------|---------|
| KEEP | C2 survived first live generalization step |
| REJECT | deterministic benefit did not transfer |
| INCONCLUSIVE | environment/provider still blocks — fix env, not mechanism |

## Forbidden

- invent PACK-v4 to “reset” without finishing T3 continuation
- edit C2 after PACK-v3 unseal
- rewrite MCID / T3 thresholds for a win
- claim live-LLM success from scripted harness smoke
- promote Trust Kernel from INCONCLUSIVE
