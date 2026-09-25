# Y20 COMPARISON_REPORT

**Protocol:** `Y20-AB-v1`  
**Prereg boundary:** `278c10d`  
**Arm A freeze:** `d6ab951`  
**Arm B freeze:** `67c682c`  
**Scored:** after both arms frozen · sealed opened only for scoring  
**Scorer/generator/budgets:** unchanged since `278c10d`

## Question answered (narrow)

> On this causal-synthetic task, under equal model/data/budget caps, what measurable
> contribution did Global OS research-loop structure provide vs a strong-agent baseline?

## Science metrics (locked scorer)

| Metric | Arm A (baseline) | Arm B (GOS loop) |
|--------|------------------|------------------|
| edge_precision | **0.722** | 0.500 |
| edge_recall | **0.684** | 0.632 |
| edge_tp / fp / fn | 13 / 5 / 6 | 12 / 12 / 7 |
| intervention_mae | **0.492** | 0.493 |
| claimed edges | 18 | 24 |

Raw: `artifacts/y20/SCORE_RAW.json`

**Reading:** On sealed science outcomes, Arm A matched or beat Arm B. Intervention MAE
is essentially tied. Dense/over-claiming in B hurt precision.

## Process metrics

| Metric | A | B |
|--------|---|---|
| human_interventions | 0 | 0 |
| dispatcher_asks | 0 | 0 |
| hypotheses_tried | 3 | **4** |
| failed_experiments | 1 | **2** |
| unsupported_claims | 0 | 0 |
| evidence_trace_completeness | 0.85 | **0.95** |
| wall_seconds_used | 120 | 180 |
| token_budget_used | 40000 | 45000 |
| tool_calls_used | 12 | 15 |
| premature_stop | false | false |
| state_loss / recovery | 0 / 0 | 0 / 0 |

**Reading:** B shows richer hypothesis/falsification trace (GOS loop artifacts present).
No reduction in human interventions vs A (both already zero in this session).
B cost slightly higher for no science gain.

## Architecture claim (honest)

```text
Global OS advantage vs strong-agent baseline on Y20 science   NOT SHOWN
(process-trace richness improved; sealed accuracy did not)
universal GOS advantage                                       NOT PROVEN
cross-domain transfer                                         NOT PROVEN
continual SI                                                  NOT MEASURED
M1.5                                                          NOT CLAIMED
```

Closest process hypothesis outcome: **H_model_alone / H_inconclusive** on science;
mild process-trace benefit without accuracy gain → **architecture complexity not
yet paid for on this task**.

## Attribution / integrity

| Item | Record |
|------|--------|
| Who chose Y20 question | Operator campaign brief + locked prereg |
| Who ran Arm A method | Agent scripts in ordinary workspace (no GOS loop files) |
| Who ran Arm B method | Agent under Goal Contract + competing Hs + durable state |
| Operator interventions mid-arm | None |
| Sealed opened before both frozen? | **No** |
| Arm B saw Arm A submission? | **No** (stated + directory discipline) |
| Contamination risk | **YES — same agent lineage authored generator in prior turn**; arms constrained to public CSV, but prior knowledge cannot be proven absent |

Integrity flag: results are usable as **directional dogfood evidence**, but a
replication with a **fresh agent that never saw the generator** would be required
before treating Y20 as clean architecture proof. Do **not** post-hoc weaken A or
retune scorer.

## What (likely) happened mechanistically

B’s GOS loop selected dense structure after rejecting sparse on an internal soft-intervention
proxy that did **not** match sealed ranking (sparse was worse on proxy; dense over-claimed
on sealed). The falsification signal was misaligned with sealed truth — a useful failure
mode of internal proxies, not a license to change the scorer.

## Next highest-value action (no dispatcher ask)

1. Keep Y20 claims frozen as above.  
2. Design **Y21** on a **different cognitive class** (prefer physical/numerical or algorithmic),
   with prereg **and** a baseline arm run by a process that never authored the generator.  
3. Optionally later: ablation C (durable checkpoint only) — still deferred.  
4. Do **not** start LH / M1.5 / Continual SI from Y20 alone.

## Non-claims

- Not “GOS lost forever”
- Not “baseline always better”
- Not Continual SI
- Not M1.5
