# Operator — T3 continuation (live keys + quota)

**Do not paste keys into chat. Do not commit keys.**

T3 remains INCONCLUSIVE. PACK-v3 is already unsealed; live runs are
**continuation of the same prereg**, not a new sealed study.

## Current blocker (2026-09-30)

`GROQ_API_KEY` works (`/models` HTTP 200) but Groq free **TPD≈200k** was
exhausted during an earlier live attempt. See
`artifacts/hardening/T3_LIVE_ATTEMPT_GROQ_TPD.md`.

## Steps

1. Restore capacity — wait for Groq TPD rolling window **or** load another free key:

```bash
# example only — use your real secret path
set -a && source /path/to/secret/.env && set +a
python3 -c "from global_os.adapters.models import live_keys_present; print(live_keys_present())"
```

Required (≥1 with remaining quota): `OPENROUTER_API_KEY` · `GROQ_API_KEY` · `GEMINI_API_KEY`

2. Confirm C2 untouched:

```bash
git diff e6dfd08 -- src/global_os/evals/trust/recovery_router.py
# expect empty (or only pre-unseal history; no post-c6523a6 edits)
```

3. Run continuation (same prereg / pack / thresholds):

```bash
cd /path/to/Global-OS
PYTHONPATH=src python3 -m global_os.evals.trust.t3_runner
```

Preflight fails closed on day-quota (`provider_quota_exhausted_live_layer`) —
it will **not** sleep for hours on TPD 429s.

4. Check artifacts:

- `artifacts/safe_autonomy_t1/T3/T3_DECISION.md` → KEEP | REJECT | INCONCLUSIVE
- `SCORE_RAW.json` → `fidelity` should be `LIVE_LLM` when quota allows; `live_preflight` present
- `LIVE_PROVENANCE.json` → provider, model, timestamps, cost, retries
- prior runs under `T3/prior_runs/` (do not delete)

## Do not

- edit `recovery_router.py` / SELECTIVE_BOUNDED_RECOVERY-v1
- rewrite T3 prereg or MCID
- create PACK-v4 “to get a clean seal”
- promote Trust Kernel from a single KEEP
- treat key-present + quota-empty as LIVE_LLM success
