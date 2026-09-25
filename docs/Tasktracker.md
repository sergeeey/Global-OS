# Tasktracker

## Done — Empirical Hardening

- [x] M0/M1 Reality Contact foundation + Empirical Science contracts (ADR-0009)
- [x] Incident system + DoD V2 evidence gate + dogfooding mission (no auto-merge)
- [x] Free pins + measured H-RSN + scheduled soak runner
- [x] Operator live smoke + live H-ENV/H-RSN JSON (claim=false)
- [x] M1.4 Trust Boundary Hardening + CI green
- [x] Local live Provider IV ≥2 → `unblocked: true` (operator Windows evidence)
- [x] Y17-1..Y17-7 real dogfood missions
- [x] Org A/B N=7 + artifact-first handoff fix for recurring info_loss
- [x] Freeze 48h program contract + PASS criteria + double gate
- [x] Compressed preflight (`make preflight-48h`)
- [x] LH-FC-PORTABILITY-SLEEP fix (Unix sleep → sys.executable; from Windows wall preflight)
- [x] Operator Windows wall preflight retry after portability fix
- [x] Wall-clock LH-v1 run completed (~42h scheduled harness PASS)
- [x] LH-v1 protocol audit (EARLY-STOP-42H + related gaps); M1.5 not closed
- [x] LH-v2 acceptance harness: T+48 barrier + duration hard gate + criteria tighten
- [x] LH-v2.1 real OS process kill + disk cold resume (`os_process_kill`)
- [x] Phase lock: LH validation deferred; return to real-world hardening
- [x] Y18 failure-mode dogfood (4 classes) + freeze diversity gate

## Done — Y19 frozen research-loop milestone (`4378005`)

- [x] Y19-RESEARCH-PROGRAM.md autonomous contract + durable resume state
- [x] Y19-H1…H7 internal steps; H5→H7 without operator dispatch
- [x] Terminal stop on `terminal_scientific_result`
- [x] Split claims: Claim A science + Claim B GOS loop (`artifacts/y19/CLAIMS.md`)
- [x] Claim B attribution honesty (bundle ≠ GOS-alone advantage)
- [x] Y19 EVIDENCE_PACK.md
- [x] Y19 FROZEN — no in-family H8 / feature-mining

## Done — Y20 A/B scored (`278c10d` prereg → COMPARISON_REPORT)

- [x] Y20 program/prereg/execution protocol + equal budgets
- [x] Arm A frozen `d6ab951` (strong baseline)
- [x] Arm B frozen `67c682c` (GOS research loop)
- [x] Unseal only after both frozen; locked scorer
- [x] COMPARISON_REPORT: science A≥B; process trace B richer; GOS advantage NOT shown
- [x] Integrity caveat recorded (generator authorship)

## Done — Y21 Mealy A/B scored (`7136808`)

- [x] Prereg locked; primary exact-match MCID 0.05; secondary cannot override
- [x] Arm A frozen `9617eb4` · Arm B frozen `ca1956d`
- [x] Unseal only after both frozen; locked scorer
- [x] Primary `TIE_WITHIN_MCID` (0.3444=0.3444); GOS sealed science gain NOT SHOWN
- [x] Process trace richer under B; COMPARISON_REPORT + CLAIMS

## Done — Y22 reliability probe scored (`f408ed1`)

- [x] Arm A `e408a28` · Arm B `5f806d0` · unseal after both frozen
- [x] Primary TIE_WITHIN_MCID (0.7146=0.7146); H_reliability_multiplier NOT CONFIRMED
- [x] COMPARISON_REPORT + CLAIMS; scorers frozen

## Active — R1 real-use (`R1-EVIDENCE-INTEGRITY-v1`)

- [x] Synthetic Y19–Y22 phase closed; **no Y23**; scorers FROZEN
- [x] R1 Goal Contract + eval rubric locked (`artifacts/r1/`, sha `d71a17f`)
- [x] Observe → hypotheses → falsify → path-binding remediations → EVALUATION
- [x] Terminal SUPPORTED; universal advantage NOT CLAIMED

## Done — R2-HDE (`H_R2`)

- [x] Hypothesis Discovery Engine on usefulness-under-null-science
- [x] REPORT + GRAPH + SEARCH_LOG under `artifacts/r2/hde/`
- [x] Y23 not recommended; discriminating test specified

## Done — R2 scientific replication (`R2-ATTN-EXPLAIN-REPLICATION-v1`)

- [x] External paper+code (Jain & Wallace 2019); contract+independent rubric locked first
- [x] CorrStats audit + extension probe; official retrain BLOCKED disclosed
- [x] Independent review scientifically_useful; decision PARTIAL; interventions=0
- [x] Ops/Docker/CRM quarantined (`artifacts/ops/SEPARATE_BACKLOG.md`)

## Done — R3 data-forensics (`R3-DATA-FORENSICS-v1`)

- [x] Dual track: campaign evidence forensics + NYC 311 sample anomalies
- [x] Independent review; FINDINGS_DELIVERED; interventions=0

## Done — failure classes + harden (`FAILURE_CLASSES_R1_R3`)

- [x] Recurring FC summary; FC-01/02/04 hardened
- [x] Compressed preflight + Linux os_kill smoke
- [x] Freeze doc + audit honesty (`FREEZE_R1_R3.md`, `AUDIT_POST_R1_R3.md`)

## Next — operator Windows / literal 48h

- [ ] Re-pin freeze SHA after harden commit
- [ ] Windows 60–120m preflight on freeze SHA
- [ ] Literal ≥48h real workload → independent audit → M1.5 candidate

## Later — after several real missions

- [ ] R2 (different class)
- [ ] Re-pin freeze SHA before any LH 96m/48h

## Deferred — True 48h / M1.5 (after new freeze)

- [ ] Windows 60–120m wall preflight on **new frozen** SHA
- [ ] Literal 48h wall on real persistent research workload (`wall_seconds >= 172800`)
- [ ] Audit → M1.5 candidate decision
- [ ] Continual SI holdout measurement (still NOT_MEASURED)
- [ ] H-ORG claim only after larger multi-class + token costs

## Deferred — True 48h / M1.5 (after freeze)

- [ ] Windows 60–120m wall preflight on **frozen** SHA
- [ ] Literal 48h wall on real persistent research workload (`wall_seconds >= 172800`)
- [ ] Audit → M1.5 candidate decision
- [ ] Continual SI holdout measurement (still NOT_MEASURED)
- [ ] H-ORG claim only after larger multi-class + token costs

## After usable Y-17 missions

- [ ] Close DoD V2 (all items PASS, not PARTIAL) when evidence warrants
- [ ] M2 H-ORG-1..4 live multi-class
- [ ] Per-capability PRODUCTION_PROVEN only with expensive evidence
