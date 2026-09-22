# Tasktracker

## Done

- [x] M0/M1 Reality Contact foundation + Empirical Science contracts (ADR-0009)
- [x] Incident system + DoD V2 evidence gate + dogfooding mission (no auto-merge)
- [x] Free pins + measured H-RSN + scheduled soak runner
- [x] Operator live smoke + live H-ENV/H-RSN JSON (claim=false; M1.5 stays IN PROGRESS)

## Active mode — Dogfood (mission → failure → fix → replay)

- [x] **Y17-1:** confirmatory Fisher replication (H-B2-1n lineage) on seeds 400–459 → **SUPPORTED**
- [x] Artifacts under `artifacts/y17/Y17-1-HB2-1n-confirmatory/` (provider IV = BLOCKED_ENVIRONMENT)
- [x] Failure cases Y17-FC-001..003 recorded
- [x] **Y17-2:** H-CAT31-V3 nested Var models → **REJECTED**; PriorWorkReframe from closed H-B7-3
- [x] Orchestrator: persist contradictory_evidence.json (regression tests)
- [ ] Y17-3 different class (prefer causal Boolean) + org A/B datapoint
- [ ] Docs drift consistency gate if warranted

## Paused — M1.5 durability (do not start 48h now)

- [ ] Persist OpenRouter `sk-or-v1-` across PS restart
- [ ] Wall-clock 48h (`GOS_REQUIRE_48H=1`) later — durability proof, not blocking dogfood

## After usable Y-17 missions

- [ ] Close DoD V2 (all items PASS, not PARTIAL) when evidence warrants
- [ ] M2 H-ORG-1..4 live multi-class
- [ ] Per-capability PRODUCTION_PROVEN only with expensive evidence
