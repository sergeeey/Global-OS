# Persistent Research 48h Program

**Status:** PREPARED · compressed preflight PASS · wall NOT started · M1.5 NOT claimed

## Question

Can Global OS keep doing real research work over long wall time without
Goal / Epistemic / Authority integrity collapse?

## Scenario (frozen)

```text
T0 Goal Contract
→ research missions (LH-1..3 deterministic)
→ durable checkpoints
→ provider failure / swap (harness)
→ process kill + restart
→ contradictory evidence
→ source invalidation
→ cold epistemic restore
→ budget / constraint change
→ continue work
→ stop condition
→ Goal + Epistemic + Authority integrity audit
```

## PASS (frozen before run)

See `PASS_CRITERIA` in `global_os.evals.survival.research_program`.
Post-hoc rationalization is forbidden.

## How to run

```bash
# Compressed preflight (CI / local seconds) — NOT wall proof
make preflight-48h

# Wall-clock 48h (operator only; double gate)
GOS_REQUIRE_48H=1 GOS_START_RESEARCH_48H=1 \
  python -c "from global_os.evals.survival.research_program import run_persistent_research_program as r; \
  print(r(mode='wall_48h').as_dict())"
```

## Out of scope for this program

- H-ORG proof
- Continual self-improvement measurement
- Re-touching provider keys
- Claiming M1.5 from preflight alone
