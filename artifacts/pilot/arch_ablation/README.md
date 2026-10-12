# Architecture Ablation — B0 vs G1/G2/G3/Gfull

**Protocol:** `ARCH-ABLATION-MECH-v1`  
**Status:** `TERMINAL` — see `DECISION.md` / `score/SCOREBOARD.json`  
**Depends on:** Pilot 3 TERMINAL · ATTR = NOT_SHOWN · M2 = CLOSED  
**Forbidden:** soften Pilot 3 ATTR; reopen M2 for optimism; PRODUCTION_PROVEN bumps

## Question

Which **minimal** Global OS mechanisms add measurable invariant protection beyond a
disciplined-but-mutable baseline (B0), under sealed long / fault / handoff / effect
scenarios?

## Arms

| Arm | Stack |
|-----|--------|
| B0 | Mutable goal + mutable checklist ledger + direct tool trust |
| G1 | Immutable Goal Contract + append-only EventLedger |
| G2 | G1 + EffectReceipt / WorldInteraction reconciliation |
| G3 | G2 + AuthorityKernel + ToolGateway fail-closed |
| Gfull | G3 + DurableRunner crash-resume + artifact-first handoff |

## Scenarios

| Id | Stress |
|----|--------|
| S1 | Long-running silent goal mutation |
| S2 | Fault + attempted negative-result erasure |
| S3 | Control handoff privilege expansion + info loss |
| S4 | ToolSuccess ≠ WorldSuccess (false external effect) |

## Fidelity

`SCRIPTED_MECHANISM_ABLATION` — deterministic in-process adversarial harness using
existing GOS primitives (ADR-0009 eval harness).  
**Not** an LLM field replication of Pilot 3. Does **not** overturn Pilot 3 ATTR.

## Artifacts

- `PREREG.md` · `LOCK.json` · `METRICS.md` · `SCENARIOS.md` · `FIDELITY.md`
- Harness: `src/global_os/evals/research/arch_ablation.py`
- Tests: `tests/test_arch_ablation.py`
- Score: `score/SCOREBOARD.json`
- Terminal: `DECISION.md`
