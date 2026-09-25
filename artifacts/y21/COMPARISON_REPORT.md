# Y21 COMPARISON_REPORT

**Protocol:** `Y21-AB-v1`  
**Prereg boundary:** `7136808`  
**Arm A freeze:** `9617eb4`  
**Arm B freeze:** `ca1956d`  
**Scored:** after both arms frozen · sealed opened only for scoring  
**Scorer / MCID / budgets / generator:** unchanged since prereg lock

## Question answered (narrow)

> On this algorithmic Mealy reverse-engineering task, under equal model/data/budget
> caps, did Global OS research-loop structure improve **primary** sealed exact-match
> performance vs a strong-agent baseline?

## Primary metric (frozen)

| Metric | Arm A | Arm B |
|--------|-------|-------|
| sealed_exact_match_rate | 0.3444 (31/90) | 0.3444 (31/90) |
| hamming_accuracy (secondary science) | 0.8206 | 0.8206 |

**Primary verdict (MCID=0.05):** `TIE_WITHIN_MCID`  
→ **H_gos_primary NOT SHOWN**

Secondary metrics **do not override** this primary result.

Raw: `artifacts/y21/SCORE_RAW.json`

## Process / secondary

| Metric | A | B |
|--------|---|---|
| human_interventions | 0 | 0 |
| dispatcher_asks | 0 | 0 |
| hypotheses_tried | 2 | **4** |
| failed_experiments | 0 | **2** |
| unsupported_claims | 0 | 0 |
| evidence_trace_completeness | 0.80 | **0.95** |
| wall_seconds_used | 240 | 300 |
| token_budget_used | 35000 | 40000 |
| tool_calls_used | 10 | 14 |
| premature_stop | false | false |
| state_loss / recovery | 0 / 0 | 0 / 0 |

**Reading:** Same sealed science; B richer falsification trace at slightly higher cost.

```text
science ≈ same
trace B > A
cost B > A
```

## Architecture claim (honest)

```text
GOS primary sealed science gain (Y21)     NOT SHOWN (tie)
GOS process-trace richness                EVIDENCE YES
Universal advantage                       NOT SHOWN
Cross-domain transfer of GOS science win  NOT SHOWN
Continual SI                              NOT MEASURED
M1.5                                      NOT CLAIMED
```

## Attribution / integrity

| Item | Record |
|------|--------|
| Sequence A→freeze→B→freeze→unseal | Honored |
| Arm B saw Arm A submission? | No |
| Sealed before both frozen? | No |
| Generator author ≠ arm runner? | Not fully (same lineage at prereg; public-only arms) |
| Integrity | DIRECTIONAL |

## Combined with Y20

| Campaign | Class | Primary science |
|----------|-------|-----------------|
| Y20 | causal synthetic | A ≥ B (GOS no sealed win) |
| Y21 | algorithmic Mealy | A = B within MCID (GOS no sealed win) |

## Next highest-value action

1. Freeze Y21 claims (done in `CLAIMS.md`).  
2. Y22 third class **or** clean-attribution replication.  
3. Do not start LH / M1.5.  
4. Do not retune Y20/Y21 scorers post hoc.

## Non-claims

Not “GOS cannot help” · Not Continual SI · Not M1.5
