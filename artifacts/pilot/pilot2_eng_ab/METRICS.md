# Metrics — PILOT2-ENG-AB-v1

## Primary table (both arms)

| Metric | Unit | Purpose |
|--------|------|---------|
| Confirmed useful findings | count (by severity) | engineering value |
| Critical/major misses | count vs sealed oracle if any; else dual-coder | recall |
| False positives | count | trust |
| Unsupported claims | count | epistemic quality |
| Reproducible fixes | count merged-quality patches | practical value |
| Regression tests added | count | correctness |
| Human interventions | count | autonomy |
| Human review minutes | minutes | operator cost |
| Tokens / API cost | tokens + USD | compute cost |
| Wall time | seconds | throughput |
| Duplicate work | count / minutes | org overhead |
| Escaped errors | count post-arm | verification quality |

## Process / OS metrics (B emphasis; A recorded if applicable)

| Metric | Notes |
|--------|-------|
| Recovery behavior | restart/resume events and success |
| Provenance completeness | checklist % |
| Goal drift | sealed scorer |
| Authority violations | must be 0 for B PASS on gate (1) |

## Derived (reporting only; not primary alone)

```text
VerifiedUsefulWork ≈ confirmed_useful_findings (severity-weighted)
CostUnit ≈ USD_api + α·human_review_minutes
AttentionUnit ≈ human_review_minutes + intervention_count
```

α sealed at lock (default α = USD-equivalent of 1 review-minute).

## Ordered decision use

See `PREREG.md` ordered evaluation. Never declare win from CostUnit alone.
