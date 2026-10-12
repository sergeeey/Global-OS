# ROADMAP.md

## Honesty

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

$$
\boxed{Implement \rightarrow Measure \rightarrow Falsify \rightarrow Learn}
$$

Track states in `docs/capability_matrix.json` **per capability** (not one sticker for whole OS).  
Architecture V2: `SPEC-ADDENDUM-V2.md`.  
**ADR-0009:** no new T0/T1 layers until M1.5 — Empirical Science phase.  
**ADR-0010:** M1.4 Trust Boundary Hardening before 48h / M1.5 claim.

## Path (locked)

Binding claim language: `docs/SCIENTIFIC_HONESTY_MAP.md`.  
**NULL ≠ zero effect.** Raw-capability amplification is **NOT SHOWN** (not “proven impossible”).

```text
CURRENT — post architecture ablation (ARCH-ABLATION-MECH-v1 TERMINAL)
  VERIFIED: disciplined audit workflow > strong baseline A; GOS can run it;
            Pilot 2 external merge + CI_VERIFIED;
            scripted mechanism layers (G1→Gfull) beat mutable B0 on S1–S4
  ATTR (Pilot 3 C vs B): PROCESS_DISCIPLINE_SUFFICES — GOS incremental NOT_SHOWN (frozen)
  Ablation: H-ABL-G1/G2/G3/Gfull SUPPORTED at SCRIPTED_MECHANISM_ABLATION fidelity
            — does not overturn Pilot 3 ATTR; see artifacts/pilot/arch_ablation/DECISION.md
  Substrate: MINIMAL-STACK-v1 LOCKED — DEFAULT=G1+G2+G3 (foundation; stop micro-reproving)
            artifacts/pilot/minimal_stack/MINIMAL_STACK_CONTRACT.md
  Mission: Autonomous Goal Achiever (substrate = inescapable core, not the product)
  Paradigm: artifacts/pilot/cognitive_core/PARADIGM.md
  Next: Cognitive Core organs + lock CHALLENGE-GA-v1 (open multi-phase goal)
  M2 CLOSED; Pilot 3 ATTR NOT_SHOWN (audit); do not soften / do not platform-only swap
  Do NOT invent M-EXT6 / ScienceKernel / Trust Kernel promote
  Y20–Y22: primary-outcome advantage NOT SHOWN
  External: PhaseBreak RECONCILED; mcp-bouncer RECONCILED+CI_VERIFIED; Pilot 3 TERMINAL
        │
        ▲ historical path (complete) ▼
M1.5 CLOSED_SCOPE_LIMITED (LH-COGNITIVE-v1)
  EXAM_SHA 7ab345e · AUDIT_SHA a7960d9 · wall_seconds≥172800 · audit all_gates_passed
  Decision: artifacts/hardening/M15_DECISION.md
        │
        ▼
Post-M1.5 — T1 REJECT · T2 KEEP · T3 KEEP once (LIVE_LLM) · Trust Kernel NOT promoted
        │
        ▼
Later (evidence-gated only): DoD V2 · Continual SI · PRODUCTION_PROVEN
  M2 H-ORG remains CLOSED until ATTR-class evidence shows incremental value beyond discipline
```

## M0 — Trustworthy Skeleton — done

## M1 — Reality Contact — nearly closed

- [x] Durable/Authority/Docker/OTLP/models×2/survival×13/multi-provider/accelerated 48h
- [x] Goal Integrity Score · H-ENV/H-RSN/H-ORG-1..4 contracts · 48h schedule · self-audit
- [x] Incident system · DoD V2 evidence gate · dogfooding mission (no auto-merge)
- [ ] Live H-ENV / H-RSN deferred until after M1.4
- [ ] Wall-clock 48h deferred until after M1.4

## M1.4 — Trust Boundary Hardening (ADR-0010)

```text
✓ CI green (numpy/scipy in [research], lockfile, pinned Temporal CLI, no /workspace abs paths)
✓ proposal-bound ExecutionToken + Gateway verify_and_consume
✓ ledger stores token_id/hash only (no raw bearer)
✓ ApprovalService.verify_and_consume on Authority path
✓ immutable claim/evidence insert
✓ cold-restart EpistemicStore.restore_from_ledger
✓ effect reconciliation statuses (OBSERVATION_PENDING / RECONCILED / DISCREPANCY / ESCALATION)
```

Acceptance: `tests/test_m14_trust_boundary.py`.  
**Not claimed complete until CI on main is green.**

## M1.5 — Long-Horizon Reality Validation — CLOSED_SCOPE_LIMITED

```text
✓ LH-COGNITIVE-v1 Windows wall PASS (EXAM_SHA 7ab345e, wall_seconds≥172800)
✓ Independent audit PASS (AUDIT_SHA a7960d9)
✓ Decision: artifacts/hardening/M15_DECISION.md
✓ 5d15600 durability ENV path retained as supporting evidence only
```

Still **≠** PRODUCTION_PROVEN / Continual SI / universal advantage.  
**LH-v1 historical:** ~42h early-stop retained; **not** the M1.5 close path.  
See `docs/SCIENTIFIC_HONESTY_MAP.md`. H-ORG / Continual SI / Trust Kernel remain separate.

## DoD V2

Checklist in `global_os.evals.maturity.dod_v2` — closed only when every item is PASS
(integration + adversarial), not merely “code exists”. Currently `closed=false`.

## M2 — Cognitive Organization — CLOSED (current evidence)

**Status after Pilot 3:** `CLOSED` — not “paused pending enthusiasm.”  
Pilot 3 ATTR = GOS incremental **NOT_SHOWN** vs disciplined baseline B.  
Reopening M2 requires new sealed evidence that specific org/runtime mechanisms beat B0
under architecture-ablation protocols — not another A/B that only beats undirected strong agents.

Historical intent (frozen text, not an active program):  
Strong single → manager-workers → 2-level → recursive → +independent verification → adaptive.  
H-ORG-1..4 remain research contracts, not proven superiority axioms.

## M3 — Adaptive / Recursive

observe→hypothesis→branch→tests→replay→benchmark→adversarial→human promotion→canary.  
Procedural / org / env / routing / retrieval / verification policy learning · VOI ·
counterfactual · regime · preference provenance. T0/T1 never self-promoted.

## PRODUCTION_PROVEN (per capability)

≥10 long-horizon runs · ≥3 task classes · ≥2 providers · real outage/swap/Docker/OTLP ·
0 unauthorized effects · 0 silent authority/sandbox fallback · 100% effects reconciled ·
corrupted recovery · malicious containment · provenance · operator use · postmortems ·
independent audit.

## Dogfooding / incidents / self-audit

- Dogfood: observe→…→request_merge; **autonomous merge forbidden**
- Incidents: root cause, blast radius, detection gap, why tests missed, regression, fix, residual risk
- Self-audit: Claim→Implementation→Tests→Runtime→maturity; overstated → CLAIM OVERSTATED

## Definition of Done

- M1.4: done (ADR-0010 + CI).  
- M1.5: **CLOSED_SCOPE_LIMITED** only (not production / Continual SI).  
- DoD V2 / PRODUCTION_PROVEN: **not closed** until per-item evidence gates pass.
