# COST_AND_LATENCY

| Mode | Provider | Cost accounting | Notes |
|------|----------|-----------------|-------|
| reactive / scripted | local mock | `$0` | No network |
| live | Groq `openai/gpt-oss-20b` | `force_cost_usd=0.0` | Free tier; operator gate required |

Live dual-mission wall time (this environment): ~20–30s total for SE+research.  
Per decision: typically <1s model latency + tool time.  
Tokens: recorded indirectly via provider usage when available; delivery stores `model_cycles`, `model_calls`, `model_cost_usd`.

**No paid OpenAI/Anthropic spend incurred.**  
If a paid model is required later: request an explicit USD budget before enabling.
