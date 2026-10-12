# Decomposer — Strategic Goal Decomposer contract

**Organ id:** `decomposer`  
**Status:** `CONTRACT_LOCKED`  
**Job:** Goal Contract → versioned strategy + prioritized subgoal/task DAG without executing world effects.

## 1. Input / Output

**In**
- `goal`: immutable Goal Contract snapshot (`goal_id`, `version`, `content_hash`, objective, success_criteria, invariants, non_goals, authority, risk)
- `context` (optional): domain hints, clarification answers, prior null_results (read-only)

**Out**
- `strategy_plan`:
  - `plan_id`, `goal_id`, `goal_version`, `goal_content_hash`
  - `phases[]`: ordered phases with intent + exit criteria
  - `tasks[]`: Task objects (`task.schema.json`) with `depends_on`, state `PENDING`
  - `priority_scores`: risk × value rationale (structured, not free prose alone)
  - `content_hash` of plan body

Decomposer **must not** produce ActionProposals or tool calls.

## 2. Authority

- Capabilities used ⊆ Goal Contract authority (GOS-I04).
- Cannot widen parent capabilities or mint ExecutionTokens.
- Clarification requests go through ClarificationPolicy — not silent assumption of missing constraints.

## 3. Quality criteria

| Id | Criterion |
|----|-----------|
| Q-D1 | Every Goal `success_criteria` item maps to ≥1 phase exit criterion |
| Q-D2 | Every Goal invariant / forbidden_outcome appears as a constraint on relevant tasks |
| Q-D3 | No microstep-only missions (outcome-level; see MissionAssigner rule) |
| Q-D4 | Plan `goal_content_hash` matches input goal; silent drift forbidden (GOS-I27) |
| Q-D5 | DAG acyclic; terminal phase = acceptance against Goal success_criteria |

## 4. Error handling

| Condition | Behavior |
|-----------|----------|
| Goal underspecified for Q-D1/Q-D2 | `CLARIFICATION_REQUIRED` — no fabricated criteria |
| Cycle / invalid task schema | `PLAN_REJECTED` — no partial execute |
| Attempt to mutate Goal in-place | `GoalMutationError` / refuse |
| Budget missing for large DAG | `BUDGET_UNKNOWN` or bounded stub plan + escalate |

Null/failed decomposition attempts → ledger `null_result.recorded` (GOS-I11).

## 5. Control-transfer rules

| From → To | When |
|-----------|------|
| Decomposer → **Orchestration** | Plan passes Q-D1–Q-D5; handoff envelope includes `plan_id` + hashes |
| Decomposer → **human/clarifier** | `CLARIFICATION_REQUIRED` |
| Decomposer → **stop** | Goal terminates / cancelled / forbidden outcome unavoidable |
| **Not** Decomposer → Tool Gateway | Never; no world effects |
| **Not** Decomposer → Pivot | Pivot only after an execution attempt fails |

Handoff must be artifact-first when payload is large (Gfull OPT-IN / artifact_handoff).

## 6. Executable tests

- `tests/test_cognitive_organ_contracts.py` — contract field presence + stub behavior  
- Stub: `global_os.cognition.organs.decomposer`  
  - builds phased plan from Goal  
  - refuses goal overwrite  
  - refuses transfer to tools  

## Non-claims

```text
≠ general-domain intelligence proven
≠ Challenge ready
≠ replaces OrgCompiler topology choice
```
