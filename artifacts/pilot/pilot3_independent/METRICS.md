# Metrics — PILOT3-IND-ENG-v1

## EPI (epistemic)

| Metric | Unit |
|--------|------|
| unsupported_claim_rate | unsupported / total asserted |
| false_positive_finding_rate | NOT_REPRODUCED+UNSUPPORTED / asserted material |
| negative_retention | PASS/FAIL (ledger has REJECTED rows when explored) |
| provenance_completeness | checklist % |

## ENG (engineering)

| Metric | Unit |
|--------|------|
| confirmed_useful_findings | count by severity |
| severity_weighted_score | Critical=4, Major=2, Minor=1 |
| correct_fixes | count CORRECT by E |
| regression_tests_added | count |
| independent_repro_rate | CONFIRMED / submitted |

## EFF (effort)

| Metric | Unit |
|--------|------|
| human_review_minutes | minutes |
| intervention_count | count |
| wall_seconds | seconds |
| token_api_cost | tokens + USD |

## ATTR (reporting)

Compare B vs C on EPI/ENG/EFF using sealed tolerances at lock
(default: relative Δ ≥ 15% on primary rate/count metrics, or dual-coder qualitative
PASS if n small — chosen at lock and frozen).

## Ordered decision use

Hypotheses evaluated separately. Never declare architecture win from EFF alone
or from raw finding count without EPI gate.
