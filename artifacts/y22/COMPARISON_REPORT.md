# Y22 COMPARISON_REPORT

**Protocol:** `Y22-AB-v1`  
**Prereg:** `f408ed1`  
**Arm A freeze:** `e408a28`  
**Arm B freeze:** `5f806d0`  
**Unseal:** only after both arms frozen  
**Weights / MCID / scorer / generator:** unchanged since prereg

## Mechanism hypothesis under test

> GOS may raise reliability/provenance/recovery on changing evidence even if it
> does not raise raw sealed exact-match science (Y20/Y21 NULL).

## Primary (frozen composite)

| Component (weight) | Arm A | Arm B |
|--------------------|-------|-------|
| final_factual_correctness (0.35) | 0.375 | 0.375 |
| invalidated_claim_cleanup (0.25) | 1.000 | 1.000 |
| unsupported_claims_score (0.20) | 0.667 | 0.667 |
| recovery_fidelity (0.20) | 1.000 | 1.000 |
| **reliability_composite** | **0.7146** | **0.7146** |

**Primary verdict (MCID=0.05):** `TIE_WITHIN_MCID`  
→ **H_reliability_multiplier NOT CONFIRMED**

Secondary metrics cannot override.

Raw: `artifacts/y22/SCORE_RAW.json`

## Process / secondary

| Metric | A | B |
|--------|---|---|
| human_interventions | 0 | 0 |
| dispatcher_asks | 0 | 0 |
| hypotheses_tried | 1 | **4** |
| failed_experiments | 0 | **3** |
| evidence_trace_completeness | 0.75 | **0.95** |
| wall_seconds / tokens / tools | 180 / 25k / 8 | 240 / 35k / 12 |

Profile again:

```text
science/reliability primary ≈ same
trace B > A
cost B > A
```

## Architecture reading (honest)

```text
Y20 raw sealed science advantage           NULL
Y21 cross-domain raw sealed advantage      NULL
Y22 reliability-composite advantage        NULL (tie)
GOS process-trace richness                 EVIDENCE YES (recurring)
Universal advantage                        NOT SHOWN
```

On this mechanism probe, GOS loop selected the same effective policy as the
strong baseline (`last_wins`) after internal discrimination — richer process,
no primary composite gain.

## Integrity

| Check | Result |
|-------|--------|
| A→freeze→B→freeze→unseal | Honored |
| B read A submission? | No |
| Weights/MCID changed after A? | No |
| Generator authorship caveat | Same lineage at prereg; public-only arms |

## Next

- Freeze Y22 claims; do not retune composite weights post hoc.  
- Map stands: seek GOS value beyond short A/B exact/reliability ties — e.g. **R1 real mission** (use track) separate from further toy rescues.  
- LH / M1.5 still deferred.

## Non-claims

Not “GOS useless” · Not Continual SI · Not M1.5 · Not weaken Arm A retrospectively
