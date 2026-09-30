# M1.5 decision — LH-COGNITIVE-v1 (LOCKED)

**Status:** `M1.5_CLOSED_SCOPE_LIMITED`  
**Decision time (UTC):** 2026-09-30T03:30:00Z (docs lock)  
**Independent audit time (UTC):** 2026-09-30T03:27:47Z

## Provenance

| Role | SHA |
|------|-----|
| **EXAM_SHA** (frozen runtime under test) | `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb` |
| **AUDIT_SHA** (freeze+audit tooling from `origin/main`) | `a7960d9616c9c08224f5be9e1e7097bca9744bd0` |

Freeze pack (operator): `artifacts/hardening/freeze_lh_cognitive_7ab345e/`  
Audit out: `artifacts/hardening/audit_cognitive_48h/out/INDEPENDENT_REVIEW.json`  
Contour: `independent_lh_cognitive_48h_v1` · `all_gates_passed=true` · failed gates: none

## Decision

**M1.5 CLOSED / scope-limited** for the following demonstrated property:

> On frozen implementation `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`, in the fixed
> Windows test environment and within LH-COGNITIVE-v1 protocol scope, Global OS
> **demonstrated** the ability to run an `EXTERNAL_RESEARCH_OBJECT` cognitive
> research workload continuously for `wall_seconds >= 172800` (observed
> `172801.2008432`), preserving the locked Goal/Epistemic/Recovery integrity
> criteria of that protocol, without mid-run modification of the runtime, and
> with independent mechanical post-run audit PASS on the frozen artifact pack.

Harness + audit agreement:

```text
fidelity              COGNITIVE_WALL_CLOCK_48H
wall_seconds          172801.2008432 >= 172800
workload_class        EXTERNAL_RESEARCH_OBJECT
report.m15_claimed    false
auditor.m15_claimed   false
m15_recommendation    M1.5_CANDIDATE_SCOPE_LIMITED → ACCEPTED as CLOSED_SCOPE_LIMITED
n_evidence_json       7
```

Prior host-reboot interruption (`_bak_reboot_interrupt_20260928_000436`) is ENV history only; the counted PASS is the full post-reboot restart.

## Explicit non-claims (binding)

This M1.5 closure does **not** establish:

- production security
- distributed exactly-once / durable external-effect semantics at production grade
- Continual Self-Improvement
- causal Global OS advantage vs a strong unstructured baseline
- universal reliability outside LH-COGNITIVE-v1 protocol scope
- that `5d15600` durability/sum harness alone was a cognitive-real 48h proof

## What changes next

Do **not** re-run the same 48h exam for celebration.

```text
Post-M1.5 (locked plan)
→ freeze SAFE_AUTONOMY_BENCHMARK-v1 + H_TRUST metrics
→ T1 A/B/C: strong agent | current GOS | GOS + Mission Assurance + bounded recovery
→ KEEP/REJECT
→ see artifacts/hardening/NEXT_MECHANISM_MISSION_ASSURANCE.md
```

Separate interesting question (not automatic claim of this M1.5):

> Can GOS produce more scientifically useful work over long horizon than a strong baseline at acceptable integrity/cost?

That is the H_TRUST / safe-autonomy envelope agenda — measure, do not assume.
