# Tasktracker

## Done

- [x] M0/M1 Reality Contact foundation + Empirical Science contracts (ADR-0009)
- [x] Incident system + DoD V2 evidence gate + dogfooding mission (no auto-merge)
- [x] Free pins + measured H-RSN + scheduled soak runner
- [x] Operator live smoke + live H-ENV/H-RSN JSON (claim=false; M1.5 stays IN PROGRESS)

## Active mode — M1.4 Trust Boundary Hardening (before more dogfood/48h)

- [x] CI: remove `/workspace` abs paths; numpy/scipy `[research]`; lockfile; Temporal CLI pin
- [x] Proposal-bound ExecutionToken + Gateway verify
- [x] Ledger: no raw bearer (token_id/hash only)
- [x] ApprovalService.verify_and_consume on Authority path
- [x] Immutable claims/evidence + cold-restart epistemic restore
- [x] Effect reconciliation statuses (GOS-I13)
- [x] ADR-0010 + ROADMAP M1.4
- [x] CI green on `main` (evidence: 4ebd062)
- [ ] Local (≥2 free keys) live provider-IV → `unblocked: true`
- [ ] Y17-6/7 + Org N↑ with token/cost (H-ORG still not claimed)
- [ ] 48h persistent research program (only after M1.4 + local IV)

## Paused — M1.5 durability (do not start 48h now)

- [ ] Persist OpenRouter `sk-or-v1-` across PS restart
- [ ] Wall-clock 48h (`GOS_REQUIRE_48H=1`) later — durability proof, not blocking dogfood

## After usable Y-17 missions

- [ ] Close DoD V2 (all items PASS, not PARTIAL) when evidence warrants
- [ ] M2 H-ORG-1..4 live multi-class
- [ ] Per-capability PRODUCTION_PROVEN only with expensive evidence
