# Fork B Phase 1 — Operator Tool Wiring

**Status:** `READY_FOR_HUMAN_REVIEW`  
**Date:** 2026-10-14  
**Branch:** `cursor/fork-b-operator-tool-wiring-2907`  
**Scope:** Close CTC ↔ ToolGateway gap on PREPROD_SUPERVISED Operator path.  
**Not claimed:** pre-production ready, Challenge-GA, live LLM, PRODUCTION_PROVEN.

## Problem (from preprod readiness audit)

Operator observe used a hardcoded `repo.audit` call. Execution Brief / Goal capabilities did not drive tool selection. A second Goal Contract could not share the same path without code edits.

## What shipped

| Piece | Location | Role |
|-------|----------|------|
| Capability → tool catalog | `src/global_os/runtime/preprod/tool_catalog.py` | Explicit `repo.audit` / `repo.inventory` specs; fail-closed resolve/assert |
| Second read-only tool | `src/global_os/world/tools/repo_inventory.py` | Top-level listing + independent verifier |
| Inventory Goal Contract | `examples/goal_repo_inventory.json` | Distinct criteria from audit Goal |
| Mock action provider | `src/global_os/adapters/models/scripted_action.py` | ≥2 sequential action cycles; $0; no network |
| Operator path | `supervised_mission.py` | `brief_select` → `gateway_observe` → `achiever_settle` → `deliver` |

No new ToolKernel, Authority surface, or T0/T1 architecture (ADR-0009).

## Actual execution path

```text
Goal Contract
  → CTC Execution Brief (allowed_tools ⊆ goal caps)
  → resolve_allowed_tool_ids(goal ∩ brief ∩ catalog)
  → ScriptedActionProvider (+ RecordingModelProvider) cycles
  → assert_tool_permitted (unknown/forbidden → fail-closed)
  → AuthorityKernel.decide → ToolGateway.execute
  → tool-specific produce + verify
  → EffectReceipt binds only criteria supported by that tool
  → Achiever + Completion Gate (independent)
  → delivery.json
```

## Evidence run (local)

```text
python3 -m pytest tests/test_preprod_supervised_mission_e2e.py -q
→ 25 passed
```

Covered:

- Audit Goal + Inventory Goal through **one** Operator workflow (no hardcoded tool branch).
- `model_cycles >= 2` via mock provider (no paid live calls).
- Negatives: tool failure, discrepancy, corrupt/empty artifact, zero budget, forbidden/unknown tool, capability deny, unsupported criteria → UNKNOWN/PARTIAL (never false SUCCESS).
- Pause/cancel; crash-resume after `gateway_observe` without silent tool replay.
- Completion Gate remains independent of catalog wiring.

## Honesty limits

- Mock/scripted model only — not a live LLM Operator.
- Catalog is a minimal explicit map (two read-only tools), not a general ToolKernel.
- Preprod / Challenge-GA / external writes: **not** claimed or started.
- Autonomous merge: **not** performed.

## Terminal

```text
READY_FOR_HUMAN_REVIEW
```
