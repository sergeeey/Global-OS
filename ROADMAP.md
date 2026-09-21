# ROADMAP.md

## Honesty

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Track states in `docs/capability_matrix.json`.  
Architecture V2: `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**  
**ADR-0009:** architecture freeze until M1.5 — phase is Empirical Science, not new layers.

## M0 — Trustworthy Skeleton

- [x] Contracts, CI pins, Goal/Event/Authority/Gateway, Survival process-kill
- [x] EnvironmentCompiler + ChangeGate + MissionAssigner
- [x] Epistemic graph (Observation→…→Commitment) + EvidenceCandidate (GOS-I22)
- [x] Synthetic H-ENV/H-RSN/H-EVAL/H-CTX harnesses (`INCONCLUSIVE_NEEDS_REAL_MODEL`)

## M1 — Reality Contact (nearly closed)

Harness-verified durable path exists; **PRODUCTION_PROVEN not claimed**:

- [x] TemporalBridge / Postgres / OTel spans / Rust Authority (RUNTIME_VERIFIED_*)
- [x] Production profile → Rust Authority fail-closed (ADR-0007)
- [x] Strong sandbox fail-closed port (ADR-0006; live Docker CI optional)
- [x] Survival suite expanded (13 RUNTIME_INJECTED)
- [x] Docker Reality Contact path + CI (`run_sandboxed_task`, GOS_REQUIRE_DOCKER)
- [x] OTLP Reality Contact path + CI collector compose (GOS_REQUIRE_OTLP)
- [x] Real model provider adapters ×2 + event trail (wire; live keys optional)
- [x] Remaining survival: malicious_document / human_rejection / contradictory_evidence / corrupted_state
- [x] 48h durable soak harness (accelerated; wall via GOS_REQUIRE_48H)
- [x] Goal Integrity Score (hard PASS/FAIL gates; soft metrics separate)
- [x] H-ENV ladder / H-RSN VUW÷Cost / H-ORG-1..4 contracts (scientific claims false)
- [x] Wall-clock 48h injection schedule (release gate, not PR)
- [x] Capability self-audit maturity pass
- [ ] Live remote model H-ENV / H-RSN when keys available
- [ ] Wall-clock 48h operational evidence (`GOS_REQUIRE_48H=1`)

## M1.5 — Operationally Validated (next gate)

Before M2 science claims:

```text
✓ real-model H-ENV run
✓ real-model H-RSN run
✓ 48h real wall-clock + scheduled injections
✓ real provider outage/recovery + model switch
✓ Docker isolation + OTLP collector active
✓ 13 survival + corrupted + malicious isolation
✓ no authority bypass; evidence/replay intact
✓ Goal Integrity Score = PASS on hard gates
```

Dogfooding: observe → analyze → propose → branch → test → verify → **request merge**  
(no autonomous merge of trusted-core).

## M2 — Cognitive Organization (after M1.5)

Question: can we organize intelligence better than one strong model?

- [x] OrganizationalUnit + MissionContract + OrgCompiler ≥3 topologies (GOS-I30)
- [x] GoalDriftDetector (GOS-I27)
- [x] H-ORG-1..4 hypothesis split (specialization / hierarchy / independent plane / adaptive distribution)
- [ ] Live multi-class evidence for H-ORG-1..4 (`scientific_claim_accepted` only with thresholds)
- [ ] InformationLoss_hierarchy on real artifacts
- [ ] Adaptive compiler on mixed task distribution

## M3 — Recursive Adaptation

- Preference Ledger / Counterfactual / VOI
- Regime detection + gated self-improvement (no T0 self-promote)

## PRODUCTION_PROVEN (expensive; not a single 48h)

≥10 long-horizon real runs · ≥3 task classes · ≥2 providers · 0 unauthorized material effects ·
0 silent authority/sandbox fallback · 100% material actions reconciled · recovery from injections ·
provenance intact · real operator usage · incidents/postmortems · independent audit.

## Definition of Done

См. `SPEC.md` + `SPEC-ADDENDUM-V2.md` §92–93.  
DoD Architecture V2 / PRODUCTION_PROVEN / M1.5 **not claimed**.
