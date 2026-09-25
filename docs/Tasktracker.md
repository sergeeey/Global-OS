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

## Active — True 48h proof (LH-v2.1)

- [x] Compressed preflight LH-v2.1
- [ ] Windows 60–120m wall preflight (LH-v2.1)
- [ ] Full wall run with `wall_seconds >= 172800` required for `WALL_CLOCK_48H`
- [ ] Continual SI holdout measurement (still NOT_MEASURED)
- [ ] H-ORG claim only after larger multi-class + token costs

## Gate — M1.5 durability

- [x] LH-v1 scheduled harness evidence recorded (not literal 48h)
- [ ] Literal 48h wall PASS under LH-v2 protocol
- [ ] Closure review only after true 48h + remaining checklist
- [ ] On FAIL: classify → minimal fix → regression → compressed replay → new 48h

## After usable Y-17 missions

- [ ] Close DoD V2 (all items PASS, not PARTIAL) when evidence warrants
- [ ] M2 H-ORG-1..4 live multi-class
- [ ] Per-capability PRODUCTION_PROVEN only with expensive evidence
