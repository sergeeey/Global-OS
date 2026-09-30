# T3 CONTINUATION — same prereg, not a new sealed replication

**Status:** `AWAITING_LIVE_KEYS`  
**Protocol:** `SAFE_AUTONOMY_T3-v1` (unchanged)  
**JSON:** `T3_CONTINUATION.json`

## Binding facts

```text
PACK-v3 was unsealed at SHA c6523a6.
Live execution was blocked by missing provider credentials.
No C2 / harness / decision-rule changes were made after unseal.
Subsequent live run is a continuation of T3 under the same prereg,
not a new sealed replication.
```

## Interpretation

| Item | Status |
|------|--------|
| T2 C2 on deterministic PACK-v2 | KEEP |
| T3 generalization | INCONCLUSIVE |
| Reason | `provider_key_unavailable_live_layer` |
| C2 | unchanged (pin `e6dfd08`) |
| Trust Kernel | not promoted |
| live-LLM claim | not established |
| PACK-v4 | **not created** — finish T3 continuation first |

T3 is a **correctly stopped experiment**, not a failed mechanism test.

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
1. Load live provider credentials locally (never commit; never paste into chat)
   - preferred free tier: OPENROUTER_API_KEY and/or GROQ_API_KEY and/or GEMINI_API_KEY
2. Do not change C2 / SELECTIVE_BOUNDED_RECOVERY-v1
3. Do not change T3 prereg / thresholds / PACK-v3
4. Run:
   PYTHONPATH=src python -m global_os.evals.trust.t3_runner
5. Preserve per-run provenance: provider, model ID/version, temperature/config,
   timestamps, cost/tokens, retries, tool failures, run-state independence
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
