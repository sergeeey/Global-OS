# Global OS Operator Edition — PREPROD_SUPERVISED v0.1

Supervised pre-production profile: **one operator**, **one active mission**,
read-only sandbox tools by default. Not multi-tenant SaaS. Not autonomous production.

## Prerequisites

```bash
python3 -m pip install -e '.[dev]'
# from repo root
```

Runtime data defaults to `./.gos/missions/<run_id>/`.

## One-command mission

```bash
PYTHONPATH=src python3 -m global_os.cli mission start \
  --goal examples/goal_repo_audit.json \
  --target . \
  --budget-usd 15
```

Or after `pip install -e .`:

```bash
gos mission start --goal examples/goal_repo_audit.json --target . --budget-usd 15
```

## Operator controls

```bash
gos mission status
gos mission pause --run-id <run_id>
gos mission resume --run-id <run_id>
gos mission cancel --run-id <run-id>
gos mission deliver --run-id <run_id>
```

Optional: `gos --root /path/to/.gos …` to isolate state.

## What you get on SUCCESS

`delivery.json` includes:

- Completion Gate decision (not an LLM oracle)
- Budget spent / remaining
- Effect receipt ids + artifact digest
- History summary (Achiever control events)
- Honesty flags (`production_proven=0`, Challenge NOT_STARTED)

## Recovery

Interruptions checkpoint via DurableRunner + on-disk durable gate.
Resume with `gos mission resume`. Gateway uses a stable idempotency key per run
so a completed `repo.audit` is not silently re-executed.

## Safety

- Irreversible / external write actions: **human confirmation required** (not enabled in this read-only pilot).
- Secrets must not be pasted into Goal JSON or delivery reports.
- Do not set `GOS_PROFILE=production` for this pilot unless rust Authority + secrets are provisioned.

## Challenge-GA

Still `NOT_STARTED`. Requires a separate explicit authorize. This Operator path is
orthogonal to the Challenge fixture.
