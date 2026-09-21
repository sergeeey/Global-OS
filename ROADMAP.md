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

## Path (locked)

```text
CURRENT b3d49f7+
  architecture + CI/runtime + survival×13 done; science not accepted
        │
        ▼
M1.5 REALITY VALIDATION     ← P0 now
  live H-ENV + live H-RSN + wall-clock 48h + Goal Integrity PASS
        │
        ▼
DoD V2
  every Architecture V2 invariant has integration+adversarial path
        │
        ▼
M2 COGNITIVE ORGANIZATION
  H-ORG-1..4; topology conditional on task class
        │
        ▼
M3 ADAPTIVE GLOBAL OS
  self-improve under governance (no T0/T1 self-promote)
        │
        ▼
PRODUCTION_PROVEN (per capability; expensive)
```

## M0 — Trustworthy Skeleton — done

## M1 — Reality Contact — nearly closed

- [x] Durable/Authority/Docker/OTLP/models×2/survival×13/multi-provider/accelerated 48h
- [x] Goal Integrity Score · H-ENV/H-RSN/H-ORG-1..4 contracts · 48h schedule · self-audit
- [x] Incident system · DoD V2 evidence gate · dogfooding mission (no auto-merge)
- [ ] **P0:** Live H-ENV (real models/API)
- [ ] **P0:** Live H-RSN (fixed L/M/H vs adaptive; VR fixed)
- [ ] **P0:** Wall-clock 48h `GOS_REQUIRE_48H=1` + scheduled injections + Goal Integrity

## M1.5 — Operationally Validated

```text
✓ real-model H-ENV + H-RSN
✓ 48h wall-clock + injected faults
✓ provider outage/recovery + model swap
✓ Docker + OTLP active
✓ survival×13 + corrupted + malicious
✓ Goal Integrity hard gates PASS
✓ no authority bypass; replay intact
```

Still **≠** PRODUCTION_PROVEN.

## DoD V2

Checklist in `global_os.evals.maturity.dod_v2` — closed only when every item is PASS
(integration + adversarial), not merely “code exists”. Currently `closed=false`.

## M2 — Cognitive Organization (after DoD V2)

Strong single → manager-workers → 2-level → recursive → +independent verification → adaptive.  
H-ORG-1 specialization · H-ORG-2 hierarchy · H-ORG-3 independent plane · H-ORG-4 adaptive on distribution.  
Success = compiler learns **which topology for which task class**, not “hierarchy wins”.

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

M1.5 / DoD V2 / PRODUCTION_PROVEN **not claimed** on current HEAD.
