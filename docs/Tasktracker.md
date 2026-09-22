# Tasktracker

## Done

- [x] M0/M1 Reality Contact foundation + Empirical Science contracts (ADR-0009)
- [x] Incident system + DoD V2 evidence gate + dogfooding mission (no auto-merge)
- [x] Free pins + measured H-RSN + scheduled soak runner
- [x] Operator live smoke + live H-ENV/H-RSN JSON (claim=false; M1.5 stays IN PROGRESS)

## Active mode — Dogfood (mission → failure → fix → replay)

- [ ] **Y-17-1:** one unfinished hypothesis end-to-end (no rewrite of scientific results)
- [ ] Artifacts under `artifacts/y17/<hypothesis-id>/` (mission/plan/sources/claims/experiments/nulls/verification/decision)
- [ ] Failure cases from the mission recorded (ENV/tool/verification/honesty)
- [ ] Minimal Global OS fixes only if the mission blocked; then replay

## Paused — M1.5 durability (do not start 48h now)

- [ ] Persist OpenRouter `sk-or-v1-` across PS restart
- [ ] Wall-clock 48h (`GOS_REQUIRE_48H=1`) later — durability proof, not blocking dogfood

## After usable Y-17 missions

- [ ] Close DoD V2 (all items PASS, not PARTIAL) when evidence warrants
- [ ] M2 H-ORG-1..4 live multi-class
- [ ] Per-capability PRODUCTION_PROVEN only with expensive evidence
