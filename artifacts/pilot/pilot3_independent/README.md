# Pilot 3 — Independent Engineering Validation

**Id:** `PILOT3-IND-ENG-v1`  
**Status:** `LOCKED` — target Paperclip@47c232b; arms not started  

**Predecessor:** Pilot 2 `PARTIAL_SUPPORT_PROCESS_ONLY` under `SAME_EXECUTOR_DUAL_PROTOCOL`  
**Product thesis under test:** evidence-backed repository auditing — **which value is GOS runtime vs process discipline alone?**

```text
Pilot 2 closed (process-only partial)
        ↓
mcp-bouncer fixes → WorldInteraction (PROPOSED / human push)
        ↓
Pilot 3 prereg (this pack) — A/B/C + blind D
        ↓
Lock → execute → blind eval → DECISION
        ↓
Value attribution (key: C vs B) → simplify or keep GOS components
```

## Arms

| Arm | Role |
|-----|------|
| **A** | Strong single agent (ordinary audit) |
| **B** | Disciplined single agent (checklist + ledger + sealed repro; no GOS runtime) |
| **C** | Full Global OS protocol + runtime |
| **D** | Independent blind evaluator |

Key comparison: **C vs B**. Beating A alone is not enough.

| File | Role |
|------|------|
| `GOAL_CONTRACT.md` | Goal + H-PILOT3-EPI/ENG/EFF + ATTR |
| `PREREG.md` | Fidelity, pins, ordered eval, terminals |
| `ABLATION.md` | Arm B discipline baseline |
| `FIDELITY.md` | Why Pilot 2 cannot prove architecture superiority |
| `FINDING_RUBRIC.md` | Confirmed-useful + blind eval (D) |
| `METRICS.md` | EPI / ENG / EFF scoreboard |
| `LOCK_CHECKLIST.md` | Gate before arms |
| `LOCK.json` | Filled at lock |
| `RUN_STATE.md` | Lifecycle |

Not M2. Not new T0/T1. Not Trust Kernel. `PRODUCTION_PROVEN = 0`.
