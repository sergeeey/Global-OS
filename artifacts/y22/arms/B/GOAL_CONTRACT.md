# Arm B Goal Contract — Y22

**goal_id:** Y22-ARM-B-EVIDENCE  
**prereg_boundary:** f408ed1  
**model_pin:** composer-cloud-agent-bundle (same as A)

## Objective

On the same public evidence stream, produce final answers + cleaned claims under
GOS research discipline (competing hypotheses → falsify on protocol-internal
checks → terminal stop). Maximize reliability behaviors without sealed peek.

## Invariants

- Do not open `artifacts/y22/sealed/`
- Do not read Arm A `submission.json`
- Do not change weights/MCID/scorer/generator/event stream
- Equal caps with Arm A

## Stop

After internal hypothesis discrimination, write submission and stop.
