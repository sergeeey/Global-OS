# ADR-0009 — Empirical Science freeze (post–M1 Reality Contact)

## Status

Accepted — 2026-09-21

## Context

M1 Reality Contact delivered Docker/OTLP CI, dual model adapters, 13 survival
injections, multi-provider verification, accelerated 48h soak, and an H-ORG
measurement pipeline with `scientific_claim_accepted=false`.

Further architectural features would dilute evidence. The open gap is empirical:
live-model H-ENV/H-RSN, wall-clock 48h with scheduled faults, and conditional
org-science (H-ORG-1..4) — not another kernel layer.

## Decision

1. **Architecture freeze (soft):** no new T0/T1 subsystems or capability surfaces
   until M1.5 *Operationally Validated* gates are met, except bugfixes, evidence
   harnesses, eval contracts, and honesty/maturity tooling.
2. Introduce milestone **M1.5 — Operationally Validated** (see ROADMAP) as the
   sole path between M1 and M2. `PRODUCTION_PROVEN` remains expensive and
   post–M1.5 (multi-run, multi-class, multi-provider, independent audit).
3. Replace averaged vanity scores with **Goal Integrity Score**: hard PASS/FAIL
   invariant gates; soft quality/cost metrics reported separately.
4. Split H-ORG-001 into **H-ORG-1..4** (specialization, hierarchy, independent
   plane, adaptive topology on task *distribution*).
5. Wall-clock 48h is a **release/nightly gate**, not PR CI; accelerated soak
   remains for PR.

## Consequences

+ Forces Architecture → Empirical Science transition.
+ Prevents premature PRODUCTION_PROVEN / hierarchy-wins claims.
− Slows feature velocity until live keys + long runs exist.
− Dogfooding stays propose→branch→human merge (no autonomous merge of T0/T1).

---

## Amendment — post M1.5 CLOSED_SCOPE_LIMITED (2026-10-12)

**Status:** Accepted addendum (does not reopen M1.5 exam).

M1.5 is `CLOSED_SCOPE_LIMITED` (`artifacts/hardening/M15_DECISION.md`). That is
**not** a license for unbounded T0/T1 kernel growth.

### Now allowed without a new T0/T1 ADR

1. **Adapter deepenings** (TemporalBridge patterns, model HTTP/scheduler, sandbox
   runner hardening) that preserve fail-closed boundaries.
2. **T2 skill packs** (SOP templates, mission stage packs) gated by eval.
3. **Eval / evidence / honesty tooling** (unchanged from original Decision §1).

### Still requires a dedicated ADR + human merge

- New T0/T1 kernel subsystems or capability surfaces (Authority rewrite,
  Epistemic kernel redesign, new privileged promotion paths).
- Trust Kernel / production-profile claims.
- Any `PRODUCTION_PROVEN` maturity bump.

Competitor-primitive borrow policy: **ADR-0013**.
