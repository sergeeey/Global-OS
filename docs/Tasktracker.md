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

## Active — Scientific dogfood (Y19); LH deferred

- [x] Y18 failure-mode dogfood (4 classes SUPPORTED)
- [x] Intermediate stable point `bfa58a0` + Linux os_kill smoke
- [x] Y19-H1 TZ + harness + acceptance tests
- [x] Y19-H1 pilot mission executed (`REJECTED` — honest MCID miss; not infra failure)
- [x] Windows `os_process_kill` smoke on exact `bfa58a0` (PASS; PIDs distinct)
- [x] Y19-H1 pilot (`REJECTED` — spectral MCID miss)
- [x] Y19-H2 mechanistic (`SUPPORTED` — size/entropy beat activity-only)
- [ ] Continue Y19 / further science dogfood → fixes → regressions
- [ ] Re-pin freeze SHA only after science path stabilizes

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
