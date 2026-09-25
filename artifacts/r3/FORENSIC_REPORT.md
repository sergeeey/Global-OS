# R3 FORENSIC_REPORT

**Mission:** R3-DATA-FORENSICS-v1  
**Rubric lock:** `65c2fb2` / 2026-09-25T17:15:00Z  
**Decision:** FINDINGS_DELIVERED  

## Constructed questions (Track B)

- Q1: Are unique_key values unique in the sample?
- Q2: What is missingness rate for incident_zip / descriptor?
- Q3: Are there same-second complaint bursts (possible batch load / scrape artifact)?
- Q4: Which complaint_type dominates; is concentration extreme?
- Q5: Are there closed-before-created or impossible date orderings when dates present?

## Track A — Campaign evidence trail

### A-F1 [MEDIUM] public_pack_sha256 is directory merkle, not file hash
- status: **CONFIRMED**
- impact: Operators comparing file SHA to process_log will false-alarm integrity failure.
- remediation: Document binding; optional field rename public_dir_sha256 in future missions (no Y20-22 rewrite).

### A-F2 [LOW] Sealed packs exist on disk but are gitignored (scorer-local)
- status: **CONFIRMED**
- impact: Repro machines without local sealed cannot rescore; intentional for anti-leak, must be documented in ops.
- remediation: Keep gitignore; ensure README WARNING remains (already present).

### A-F3 [MEDIUM] R1 evaluation was executor-contour; R2 introduced independent review
- status: **CONFIRMED**
- impact: R1 usefulness is weaker external validity than R2.
- remediation: Require independent review for R3+ (this mission).

### A-F4 [INFO] Y22 freeze SHAs present in Tasktracker
- status: **SUPPORTED**
- impact: None if supported; else doc drift.
- remediation: None if supported.

### A-F5 [HIGH] Tests can regenerate historical mission artifacts (provenance noise)
- status: **NOT_FOUND**
- impact: git dirty / false history during make test; contaminates forensic timestamps.
- remediation: Prefer read-only assertions on frozen artifacts; regenerate only under explicit flag (deferred if invasive).

## Track B — NYC 311 sample anomalies

- pin sha256: `4c6912dca4a3ca5b4d42fba8b6fb594112388fd28b12db58d03ddc0d3583af7e`
- n=500 snapshot (sample-relative)

### B-F1 [INFO] unique_key uniqueness in sample
- status: **OK**
- evidence: `{"n_dup_keys": 0, "examples": []}`

### B-F2 [INFO] Missing incident_zip / descriptor rates
- status: **MEASURED**
- evidence: `{"miss_incident_zip": 0.004, "miss_descriptor": 0.0}`

### B-F3 [INFO] Same-timestamp created_date bursts
- status: **CONFIRMED**
- evidence: `{"top_bursts": [["2026-09-23T23:57:47.000", 6], ["2026-09-23T23:57:46.000", 3], ["2026-09-23T23:51:40.000", 3], ["2026-09-24T01:27:47.000", 2], ["2026-09-24T00:55:56.000", 2]], "max_burst": 6}`
- note: Sample-relative; may reflect Socrata page ordering / batch writes, not fraud.

### B-F4 [INFO] complaint_type concentration
- status: **MEASURED**
- evidence: `{"top_types": [["Noise - Residential", 125], ["Illegal Parking", 88], ["Noise - Street/Sidewalk", 60], ["Noise", 49], ["Blocked Driveway", 26], ["Noise - Commercial", 21], ["Street Condition", 16], ["Noise - Vehicle", 9]], "n_types": 50}`

### B-F5 [INFO] closed_date before created_date
- status: **OK**
- evidence: `{"rows_with_closed": 176, "bad_order": 0}`

### B-H-falsified [INFO] Hypothesis: agency mostly missing
- status: **REJECTED**
- evidence: `{"miss_agency_rate": 0.0}`
- note: Constructed wrong turn; agency nearly always present.

## Minimal remediation applied
- artifacts/r3/work/SHA_BINDING_NOTE.md (docs-only; no T0/T1; no frozen arm rewrite)

## Non-claims
No GOS advantage · No M1.5 · No Continual SI · No population inference from n=500

