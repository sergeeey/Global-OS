# Global OS Operator Edition — PREPROD_SUPERVISED v0.1

Supervised pre-production profile: **one operator**, **one active mission**,
sandbox tools via ToolGateway. Not multi-tenant SaaS. Not autonomous production.

## Prerequisites

```bash
python3 -m pip install -e '.[dev]'
# from repo root; or use PYTHONPATH=src without install
```

Runtime data defaults to `./.gos/missions/<run_id>/`.

## One-command mission (observation-reactive mock — default)

```bash
PYTHONPATH=src python3 -m global_os.cli mission start \
  --goal examples/goal_repo_audit.json \
  --target . \
  --budget-usd 15 \
  --model reactive
```

Software-engineering sandbox + research examples:

```bash
PYTHONPATH=src python3 scripts/preprod_run_missions.py --model reactive
```

## Live LLM (Groq free tier — operator gated)

Requires `GROQ_API_KEY` and explicit authorization:

```bash
export GOS_AUTHORIZE_LIVE_LLM=1
PYTHONPATH=src python3 -m global_os.cli mission start \
  --goal examples/goal_research_scan.json \
  --target /path/to/corpus \
  --model live \
  --authorize-live-llm \
  --budget-usd 5
```

Default live model: `openai/gpt-oss-20b` (`GOS_OPERATOR_LIVE_MODEL` override).  
Recorded adapter cost is `$0` on Groq free tier. **Do not enable paid providers without a separate budget authorize.**

## Operator controls

```bash
gos mission status
gos mission pause --run-id <run_id>
gos mission resume --run-id <run_id>
gos mission cancel --run-id <run_id>
gos mission deliver --run-id <run_id>
```

Optional: `gos --root /path/to/.gos …` to isolate state.

## Recovery probe (real process kill)

```bash
PYTHONPATH=src python3 scripts/preprod_real_kill_recovery.py
```

## What you get on delivery

`delivery.json` includes Completion Gate decision, budget, receipts, model_mode/cycles/cost, honesty flags.

## Safety

- World effects only via ToolGateway after Authority.  
- Irreversible external systems: not enabled beyond sandbox target writes.  
- Challenge-GA: `NOT_STARTED` without separate authorize.  
- Do not set `GOS_PROFILE=production` unless rust Authority + secrets are provisioned.

## Acceptance pack

`artifacts/preprod/final_acceptance/` + `artifacts/preprod/PREPROD_RELEASE_GATE.md`
