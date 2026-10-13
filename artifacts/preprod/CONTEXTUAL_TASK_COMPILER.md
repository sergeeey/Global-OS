# Contextual Task Compiler (v0)

Ephemeral **Execution Briefs** for Achiever steps — not a prompt library.

## Constant vs generated

| Constant | Generated per step |
|----------|-------------------|
| Goal Contract | `objective_text` for the step |
| Authority / caps | `allowed_tools` ⊆ caps |
| Completion Gate rules | `criterion_ids` (scoped subset) |
| Human approval policy | Brief prose + structured fields |

## Flow

Goal + Decomposer plan + EnvironmentCompiler → `compile_execution_brief` → route/attempt → Completion Gate.

Briefs emit on material reasons only (`first_attempt`, `pivot`, …). They never certify `SUCCEEDED`.

## Operator note

`delivery.json` may include `last_execution_brief` for audit. Treat it as a work order, not proof of goal achievement.

## Fail-closed routing

If an Execution Brief has `allowed_tools=[]`, Achiever **stops** with an error.
It must not invent `filesystem.read` (or any other capability) to continue.

## Non-claims

- Not PromptKernel / PromptOS
- Not Continual SI / PRODUCTION_PROVEN
- A/B/C outcome metrics: NOT_MEASURED until a dedicated pilot
- Challenge-GA: NOT_STARTED
