# Arm B Goal Contract — Y21

**goal_id:** Y21-ARM-B-MEALY  
**prereg_boundary:** 7136808  
**model_pin:** composer-cloud-agent-bundle (same as A)

## Objective

Predict sealed Mealy holdout outputs from public traces under equal caps,
using Global OS research discipline.

## Invariants

- Do not open `artifacts/y21/sealed/`
- Do not read Arm A `submission.json`
- Do not change scorer/MCID/budgets/generator
- Claim strength ≤ evidence

## Stop

Terminal after competing hypotheses falsified on internal holdout, or budget wall.
