# Pivot / Replan — Failure-Driven Re-Planning contract

**Organ id:** `pivot_replan`  
**Status:** `CONTRACT_LOCKED`  
**Job:** on failed approach, record negative knowledge and produce a bounded strategy amendment — never silent Goal overwrite.

## 1. Input / Output

**In**
- `goal` snapshot (id/version/hash)
- `active_plan` (from Decomposer)
- `failure`: `{attempt_id, task_id?, phase_id?, why_failed, evidence_refs[], observation?}`
- `attempt_budget`: max pivots remaining for this goal version

**Out**
- `replan_decision`: one of
  - `PIVOT`: new/amended `strategy_plan` (new `plan_id`, supersedes prior) + rationale
  - `RETRY_BOUNDED`: same plan, same task, with explicit remaining count
  - `ESCALATE`: human / higher authority
  - `STOP`: termination condition met (budget, forbidden, success impossible)

## 2. Authority

- Amendments cannot expand Goal authority or forbidden_outcomes.
- Goal changes require GoalStore.amend (GOS-I06) — Pivot proposes; does not overwrite.
- Child retries ⊆ parent grant; no unbounded spawn (GOS-I18 / anti-storm).

## 3. Quality criteria

| Id | Criterion |
|----|-----------|
| Q-P1 | Every failure persists as `null_result` / ledger event before pivot (GOS-I11) |
| Q-P2 | PIVOT plan must differ in at least one material strategy field vs failed attempt |
| Q-P3 | No re-selection of an approach marked failed for same task without new evidence |
| Q-P4 | `attempt_budget` decrements; at 0 → ESCALATE or STOP (not infinite loop) |
| Q-P5 | Goal `content_hash` unchanged unless explicit amend protocol completed |
| Q-P6 | **Failure-informed selection:** pivot rationale must cite `why_failed` and how the new approach avoids that failure mode |

### Selection mechanism (goal progress)

Pivot is not “make another plan.” It must:

- bind `why_failed` → excluded approaches  
- name the new approach and why it better serves terminal success_criteria  
- stop when no remaining approach can advance the Goal (STOP_NO_STRATEGY)  

## 4. Error handling

| Condition | Behavior |
|-----------|----------|
| Missing failure why_failed | `INVALID_FAILURE` — refuse pivot |
| Budget exhausted | `STOP` or `ESCALATE` |
| Effect discrepancy (tool≠world) | feed as failure; do not treat tool success as done |
| Plan hash mismatch vs goal | `STALE_PLAN` — force Decomposer refresh |

## 5. Control-transfer rules

| From → To | When |
|-----------|------|
| Execution/Orchestration → **Pivot** | Task/phase failed, discrepancy, or Q-criteria miss |
| Pivot → **Orchestration** | `PIVOT` or `RETRY_BOUNDED` with remaining budget > 0 |
| Pivot → **Decomposer** | Strategy structure invalid / needs full re-phase (`STALE_PLAN` or major pivot) |
| Pivot → **human** | `ESCALATE` |
| Pivot → **terminal stop** | `STOP` or Goal termination criteria |
| **Not** Pivot → silent Goal rewrite | Forbidden |
| **Not** Pivot → Tool Gateway directly | Effects only via Orchestration → Authority → Gateway |

## 6. Executable tests

- Contract guards + stub in `tests/test_cognitive_organ_contracts.py`
- Stub: `global_os.cognition.organs.pivot_replan`
  - records failure
  - refuses repeat of same failed approach without new evidence
  - enforces attempt budget

## Non-claims

```text
≠ optimal search proven
≠ unbounded autonomy
≠ full exactly-once external effects
```
