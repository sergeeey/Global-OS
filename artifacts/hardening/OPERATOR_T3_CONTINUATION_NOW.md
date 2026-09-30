# Operator — T3 continuation (live keys)

**Do not paste keys into chat. Do not commit keys.**

T3 is INCONCLUSIVE due to missing live credentials. PACK-v3 is already unsealed;
the next live run is a **continuation of the same prereg**, not a new sealed study.

## Steps

1. Load free-tier keys into your local environment (outside git), e.g. from `.env.local` / secret store:

```bash
# example only — use your real secret path
set -a && source /path/to/secret/.env && set +a
python -c "from global_os.adapters.models import live_keys_present; print(live_keys_present())"
```

Required (≥1): `OPENROUTER_API_KEY` · `GROQ_API_KEY` · `GEMINI_API_KEY`

2. Confirm C2 untouched:

```bash
git diff e6dfd08 -- src/global_os/evals/trust/recovery_router.py
# expect empty (or only pre-unseal history; no post-c6523a6 edits)
```

3. Run continuation (same prereg / pack / thresholds):

```bash
cd /path/to/Global-OS
PYTHONPATH=src python -m global_os.evals.trust.t3_runner
```

4. Check artifacts:

- `artifacts/safe_autonomy_t1/T3/T3_DECISION.md` → KEEP | REJECT | INCONCLUSIVE
  (must still say continuation / not a new sealed replication)
- `SCORE_RAW.json` → `fidelity` should be `LIVE_LLM` when keys work; `continuation` block present
- `LIVE_PROVENANCE.json` → provider, model ID/version, temperature, timestamps, cost, retries, tool failures
- prior blocked run archived under `T3/prior_runs/` (do not delete)

## Do not

- edit `recovery_router.py` / SELECTIVE_BOUNDED_RECOVERY-v1
- rewrite T3 prereg or MCID
- create PACK-v4 “to get a clean seal”
- promote Trust Kernel from a single KEEP
