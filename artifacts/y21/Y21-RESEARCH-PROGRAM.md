# Y21 Research Program — Algorithmic Reverse-Engineering A/B

**Status:** Binding once `CURRENT_STATE.prereg_locked=true`  
**Class:** Hidden Mealy transducer I/O reverse-engineering  
**Not:** Y20 retune · document-evidence · LH · M1.5

## Terminal mission (both arms)

From observational input/output traces only, predict sealed holdout output
sequences for given inputs. Optional: claim state count.

## Primary win (frozen)

`sealed_exact_match_rate` — fraction of sealed traces with **exact** output-sequence match.

GOS primary win only if:

```text
score_B >= score_A + 0.05   (PRIMARY_MCID)
```

Secondary metrics (interventions, unsupported claims, recovery, trace completeness,
cost/wall) **must not override** a primary loss/tie.

## Arms

| Arm | Stack |
|-----|--------|
| A | Strong agent + ordinary workspace |
| B | Same model + Goal Contract + durable research loop + falsification + stop |

Equal model, public pack, tools, budgets. A not crippled.

## Sequence

```text
prereg lock → A → freeze A → B → freeze B → unseal → blind score → COMPARISON_REPORT
```

## Attribution hygiene

Ideal: generator author ≠ arm runners. If same lineage, record caveat; arms still
must not open sealed/ or mealy tables during execution.

## Hard forbids

- Change scorer/MCID/budgets/generator after prereg lock
- Unseal after A before B frozen
- Retune Y20
- Claim universal GOS advantage from Y21 alone
- LH / M1.5 / Continual SI from Y21 alone
