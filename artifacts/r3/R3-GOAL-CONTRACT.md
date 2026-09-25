# R3 Goal Contract — Data forensics / anomaly investigation

**mission_id:** `R3-DATA-FORENSICS-v1`  
**class:** real-use data-forensics / anomaly investigation  
**≠** paper replication (R2) · ≠ honesty matrix (R1) · ≠ synthetic Y-A/B  
**model_pin:** composer-cloud-agent-bundle  
**ADR-0009:** no new T0/T1 surfaces

## Why this class

Different failure pressure than R2:
- no ready paper structure / prereg tables
- must **construct** investigative questions
- provenance, parsing, anomaly hypotheses, source checks
- concrete deliverable (forensic report), not only scientific decision label

## Dual scope (locked)

### Track A — Campaign evidence-trail forensics
Investigate integrity/anomaly risks in Y19–R2 artifacts:
SHA binding semantics, sealed visibility, regeneration risk, self-score risk,
doc/SHA drift. Produce severity-rated findings.

### Track B — External open-data anomaly investigation
Dataset: NYC 311 service requests sample (`data/nyc311_sample_n500.json`,
pinned at mission start). Build questions, hunt anomalies (duplicates, time
clusters, missingness, agency/type outliers), finish with actionable notes.

## Objective (given once)

Deliver `FORENSIC_REPORT.md` + `SUBMISSION.json` with:
1. Constructed investigation questions (not inherited from a paper)
2. Findings with severity + evidence paths
3. Hypotheses tried / falsified
4. ≥1 minimal remediation **only if** ADR-0009-safe (docs/tests/honesty), else deferred
5. Terminal: `FINDINGS_DELIVERED` (always) + scientific-style status on tracks
6. Independent review under locked rubric (executor must not self-score usefulness)

## Invariants

- No invented data rows or fake anomalies
- No Y23; Y20–Y22 scorers frozen
- No CRM/Docker ops mixing (`artifacts/ops/SEPARATE_BACKLOG.md`)
- Checkpoint ≠ stop; failure → minimal fix → continue
- Independent reviewer must not read `OPEN_HYPOTHESES.md`

## Stop

SUBMISSION + FORENSIC_REPORT + independent review written; interventions logged.

## Non-goals

M1.5 · Continual SI · GOS comparative advantage claim · another paper replication
