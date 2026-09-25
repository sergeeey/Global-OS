# Arm B Goal Contract

**goal_id:** Y20-ARM-B-CAUSAL  
**version:** 1  
**prereg_boundary:** 278c10d  
**model_pin:** composer-cloud-agent-bundle (same as Arm A)

## Objective

Recover limited causal structure and predict sealed `do(X=x)` expectations from
observational public pack only, under equal budgets, using Global OS research
discipline (competing hypotheses → discriminating tests → falsification → update →
terminal stop).

## Invariants

- Do not open `artifacts/y20/sealed/`
- Do not read Arm A `submission.json` / discovery outputs
- Do not change global scorer/generator/budgets
- Equal caps with Arm A
- Claim strength ≤ evidence strength; INCONCLUSIVE allowed

## Stop when

1. Terminal narrow claim for this arm under internal validation, or
2. Low EVI for further in-arm hypotheses, or
3. Budget wall

## Out of scope

Architecture changes to Global OS core; LH; M1.5; Continual SI.
