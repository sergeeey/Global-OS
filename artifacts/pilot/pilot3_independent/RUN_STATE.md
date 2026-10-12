# RUN_STATE — PILOT3-IND-ENG-v1

**Lifecycle:** `LOCKED`

| State | Meaning |
|-------|---------|
| `PREREG_DRAFT` | Pack authored; not locked |
| `LOCKED` | Pins + executors sealed; arms may start (**current**) |
| `RUNNING` | ≥1 arm in progress |
| `EVAL_SEALED` | Blind evaluator D submitted scores |
| `TERMINAL` | DECISION.md published |

## Locked target

`sergeeey/Paperclip-AI---2026@47c232b` — focus `tools/workflow-controller`

## Next actions (ordered)

1. Execute Arms A, B, C in isolated subagent sessions (no cross-leak).
2. Anonymize → Arm D blind eval → `EVAL_SEAL.json`.
3. Unseal mapping → score EPI/ENG/EFF + ATTR (C vs B) → `DECISION.md`.

## Standing non-claims

```text
≠ M2 started
≠ PRODUCTION_PROVEN
≠ Trust Kernel promote
≠ fully independent two-lab replication (fidelity = ISOLATED_SUBAGENT_ARMS_SAME_ORCHESTRATOR)
```
