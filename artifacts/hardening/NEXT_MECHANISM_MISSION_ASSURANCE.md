# Next mechanism plan — Mission-Level Runtime Assurance + Bounded Recovery

**Status:** PLAN LOCKED (research priority) — **NOT implemented** · **NOT M1.5 claim**  
**As-of:** 2026-09-28  
**Confidence on priority:** medium-high  
**Confidence on GOS efficacy:** unknown (to measure)

## Verdict (re-check)

**Agree** with the research conclusion as the **post-M1.5 next-mechanism bet**, with these bindings:

```text
AGREE
  H1 Mission-Level Runtime Assurance + Bounded Recovery
  = strongest near-term candidate for safe usable autonomy
  NOT “another LLM judge”
  NOT implement before M1.5 decision + frozen benchmark

AGREE falsifiers
  integrity escapes ↓ but completion ↓↓ / human attention ↑↑  → REJECT (Verifier Tax 2.0)
  C ≈ B on material escapes                                 → do not integrate

AGREE order
  Metamorphic = high-value supporting Verification Fabric (not full envelope)
  Calibrated risk / selective acting = high upside, premature (no calibration base)
  Regime router = cost lever, indirect safety
  New multi-agent topology / memory = low priority now (no bottleneck evidence)

KEEP LIVE adversarial alternative
  Maybe GOS needs better tasks/external eval, not new machinery
  Y20–Y22 already weakened “more structure ⇒ better outcome”
```

Do **not** treat this as confirmed architecture. Treat as **H_NEXT / H_TRUST mechanism candidate**.

## Why this fits Global OS

Existing bricks: Goal Contract · Epistemic invalidation · Authority · EffectReceipt · Recovery.  
Missing contour: **mission-level integrity over time** (not only per-action allow/deny).

```text
strong untrusted intelligence
→ works freely under Authority
→ mission invariants continuously evaluated
→ GREEN continue | YELLOW degrade | RED repair/rollback/escalate | BLACK freeze+preserve
```

External literature supports maturity of runtime monitoring **and** the verifier-tax failure mode; therefore the package is **monitor + safe modes + bounded repair + recovery**, not monitor alone.

## Mission invariants (v1 experiment set)

```text
MI-1 Goal Integrity      — no silent goal mutate (maps goal-drift escape)
MI-2 Epistemic Integrity — stale/invalidated evidence cannot back material decisions
MI-3 Authority Integrity — continuation does not expand authority
MI-4 Effect Integrity    — ambiguous/unverified effect ≠ world_success
MI-5 State Integrity     — after recovery: material claims / nulls / commitments retained
```

Maps onto `H_TRUST` material failure taxonomy (`artifacts/hardening/H_TRUST_DRAFT.md`).

## Modes (Cognitive Simplex — experimental label only)

```text
GREEN  — normal autonomy
YELLOW — local work OK; consequential external effects restricted
RED    — bounded repair / rollback / human escalation
BLACK  — freeze mission; preserve evidence; no effects
```

Implementation constraint (falsifier if violated):

> Thin evaluator over existing events/state. If it requires rewriting half of GOS → counterevidence against incremental hypothesis.

## Assurance stack (non-negotiable)

```text
1 deterministic invariants / state+provenance queries
2 (optional) LLM semantic assist — never sole oracle
3 human only at selected boundaries
```

LLM-only mission judge is **forbidden** as the assurance core (SLEIGHT-class blind spots).

## Metrics (frontier, not one fake composite)

| Metric | Role |
|--------|------|
| **MIER** — Material Integrity Escape Rate | primary (P1) |
| **SSR** — Safe Success Rate (useful ∧ no material failure) | co-primary (P2) |
| SAH — Safe Autonomous Horizon | secondary |
| Human attention (escalations / operator minutes) | secondary |
| Utility tax (task completion drop) | secondary / falsifier |
| Cost tax (tokens / tools / latency) | secondary |

Denominators prefer consequential actions / missions, not “per hour of sleep”.

Benchmark modes remain **A fixed-resource** and **B cost-normalized** (see H_TRUST).

## Experiment T1 — SAFE_AUTONOMY_ENVELOPE (before any core integration)

```text
AFTER M1.5 decision (PASS/FAIL/INVALID does not cancel this plan)
→ FREEZE SAFE_AUTONOMY_BENCHMARK-v1 (prereg + MCID after variance pilot)
→ arms:
     A  strong agent baseline
     B  current Global OS
     C  GOS + thin Mission Assurance + bounded recovery
→ equal model/tools/tasks/data/permissions/env/time
→ fault classes: goal drift, stale evidence, invalidation, authority expand,
                 ambiguous effect, state corruption, process restart,
                 malicious instruction, cumulative multi-step violation
→ + benign matched controls (measure overblocking)
→ KEEP / REJECT by P1+P2 with utility/attention taxes
```

**No MCID before variance pilot.**  
**Null is a success** if it falsifies the mechanism.

## Sequencing vs current exam

```text
NOW
  cognitive_wall_48h on freeze 7ab345e (ENV reboot → restart allowed)
  ADR-0009: no new T0/T1 surfaces mid-exam

AFTER M1.5 decision
  1) freeze H_TRUST + SAFE_AUTONOMY_BENCHMARK-v1 metrics
  2) thin Mission Assurance experiment (T2/eval harness first; no silent T0 promote)
  3) KEEP/REJECT
  4) only then Trust Kernel hardening tied to MI-* / material failures
  5) metamorphic as Verification Fabric add-on
  6) later: risk budgets / routers if update triggers fire

OPTIONAL durability (separate)
  host-reboot checkpoint-resume for wall exams
  = ENV harness improvement; new freeze if it changes exam semantics
  ≠ substitute for Mission Assurance
```

## Structural exception

If workload becomes irreversible external effects (payments, prod deploy, email, delete, credentials, cloud mutate):

```text
durable effect semantics / idempotency / reconciliation = P0 floor
before or with mission assurance
```

Research/local cognitive exams are not that floor yet.

## Update triggers (re-rank)

| Signal | Shift |
|--------|--------|
| Metamorphic forensic finds many material semantic fails in old artifacts | Metamorphic ↑ |
| Real missions bottleneck on human review | Risk budget ↑ |
| Failures rare; cost dominates | Method router ↑ |
| Consequential external effects begin | Durable effects → P0 |

## Forbidden overclaims

- “Cognitive Simplex is next core OS layer” without T1 KEEP  
- “Runtime assurance proven for GOS” before arms A/B/C  
- Implementing under current M1.5 freeze SHA  
- LLM boolean security decisions as GREEN/RED authority

## Sources of this plan

Operator research memo 2026-09-28 (literature + competing hypotheses).  
Internal: Y20–Y22 NULL primary; R1–R3 EARLY YES bundle; H_TRUST draft; SCIENTIFIC_HONESTY_MAP.
