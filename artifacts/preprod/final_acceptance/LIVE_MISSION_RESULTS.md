# LIVE_MISSION_RESULTS

**Provider:** Groq `openai/gpt-oss-20b` via existing adapter  
**Authorization:** `GOS_AUTHORIZE_LIVE_LLM=1` / `--authorize-live-llm` (operator gate)  
**Recorded cost:** `model_cost_usd=0.0` (adapter `force_cost_usd=0.0` free tier)  
**Archives:** `missions_live/MISSIONS_SUMMARY.json`, `se_delivery.json`, `research_delivery.json`  
**Comparable mock:** `missions/MISSIONS_SUMMARY.json` (reactive, fully deterministic)

## Live run (latest)

| Mission | Terminal | Completion | Tools (order) | Cycles | Notes |
|---------|----------|------------|---------------|--------|-------|
| SE sandbox | SUCCEEDED | ACHIEVED | inventory → read → write → audit | 5 | Live chose paths; FIX_APPLIED.txt may differ from oracle filename |
| Research scan | SUCCEEDED | ACHIEVED | research.scan (+ extra reads) | 6 | Later invalid empty-args attempt recorded in observe_block |

## Reactive control (same Goals)

Both SE and research **SUCCEEDED/ACHIEVED** with criterion-matching tool sequences (5 and 2 cycles).

## Honesty

- Live autonomy demonstrated (observation-conditioned next actions, not a fixed script).  
- Live is **not** a multi-hour production soak.  
- Paid OpenAI/Anthropic not used.  
- Challenge-GA not run.  
