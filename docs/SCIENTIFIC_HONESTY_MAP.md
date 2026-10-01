# Scientific honesty map — post Y20–Y22 / R1–R3 / pre-M1.5

**Status:** Binding for claims and roadmap talk  
**Exam SHA (unchanged):** `5d15600` — do not patch for these docs

## Ladder (locked wording)

```text
Y20–Y22
  Raw primary-outcome advantage vs strong baseline?
  → NOT SHOWN
  (on the tested task classes under locked protocols)
  NULL ≠ proof of zero effect

R1–R3
  Can this configuration produce useful, checkable real work
  autonomously to a terminal/audited result?
  → EARLY YES for the tested bundle/tasks
  Causal GOS-alone advantage vs unstructured strong agent?
  → NOT MEASURED

M1.5 claim fork B (chosen) — CLOSED_SCOPE_LIMITED
  see artifacts/hardening/M15_DECISION.md
  EXAM_SHA 7ab345e · AUDIT_SHA a7960d9
  Demonstrated: EXTERNAL_RESEARCH_OBJECT cognitive wall ≥172800s + integrity gates + independent audit
  NOT demonstrated: production security, Continual SI, causal GOS vs baseline

M1.5 (cognitive path)
  Long-horizon integrity on frozen real research workload ≥48h?
  → SHOWN within LH-COGNITIVE-v1 protocol scope (not universal)

Post-M1.5
  Does a trust layer reduce predefined material integrity failures
  enough to justify operational cost?
  → CORE NEXT HYPOTHESIS (H_TRUST)
  → SAFE_AUTONOMY_BENCHMARK-v1 METRICS_FROZEN + MCID SET_BY_VARIANCE_PILOT_v1
  → T1 A/B/C DETERMINISTIC_FAULT_MISSIONS_v1 → REJECT (verifier_tax_2_0_completion)
    H_TRUST NOT CONFIRMED under pack v1 (ADR-0011)
  → T2 selective recovery on PACK-v2 → KEEP (FSR=1.0, URR=0; ADR-0012)
  → C2 frozen as SELECTIVE_BOUNDED_RECOVERY-v1 (candidate capability, not core)
  → T3 prereg LOCKED: live-LLM generalization/replication (not redesign)
    still ≠ Trust Kernel / production / universal H_TRUST
```

## Forbidden overclaims

| Do **not** say | Say instead |
|----------------|-------------|
| “GOS does not amplify intelligence” | “Raw-capability / primary-outcome amplification: **NOT SHOWN** on tested classes” |
| “R1–R3 prove GOS superiority” | “Bundle/configuration can deliver useful checkable real work; **causal GOS advantage NOT MEASURED**” |
| “M1.5 PASS ⇒ production / distributed exactly-once / universal reliability” | “PASS only within **locked protocol scope** on freeze SHA” |

## Working stance (not a proven theorem)

```text
Raw-capability amplification:     NOT SHOWN  (no longer the working project bet)
Trust / long-horizon amplification: PARTIAL (M1.5 scope-limited);
                                    H_TRUST T1 REJECT; T2 KEEP; C2 frozen;
                                    T3 KEEP once under live Groq (continuation);
                                    ≠ independent replication / production / Trust Kernel
```

We stopped treating raw-IQ amplification as the **working hypothesis** because evidence does not support it so far — not because we proved a universal null.

## M1.5 claim template (narrow)

> On frozen implementation `5d15600`, in a fixed test environment and within a
> pre-registered protocol scope, Global OS did / did not demonstrate the ability
> to run a real research workload continuously for `wall_seconds >= 172800`,
> preserving stated Goal / Epistemic / Recovery integrity properties **without
> mid-run modification of the runtime**.

Phrase **“within protocol scope”** is mandatory.

## Gate A (unchanged sequence)

```text
5d15600
→ no core changes on exam SHA
→ Windows smoke
→ Windows preflight
→ literal >=48h (hard gate 172800s; T+42 ≠ PASS)
→ freeze raw artifacts
→ independent audit
→ M1.5 decision
```

### Defect handling

```text
environmental problem
→ repair environment → document → same SHA may continue/restart as protocol allows

runtime/code defect
→ current exam FAIL/INVALID
→ no patch-and-continue on 5d15600
→ fix elsewhere → regression → new freeze SHA → new exam
```

## Post-M1.5 roadmap order (preferred)

```text
M1.5 decision
→ freeze scientific hypothesis + metrics (H_TRUST + material failure taxonomy)
→ Trust Kernel hardening (failure-mode-tied only)
→ adversarial evaluation
→ external benchmarks
→ interoperability
```

Do **not** invent metrics after building five security mechanisms.

## H_TRUST (METRICS_FROZEN — see SAFE_AUTONOMY_BENCHMARK_V1)

> **H_TRUST:** Under comparable model/tool/task conditions, Global OS reduces the
> rate of pre-defined **material integrity failures** vs a strong baseline at a
> measurable and acceptable cost in completion, latency, compute, and human review.

### Material integrity failures (pre-register before hardening)

```text
unauthorized effect
duplicate effect
false reconciliation
stale-decision escape
unsupported-conclusion escape
goal-drift escape
state-loss after recovery
unlogged operator intervention
```

### Trustworthiness Benchmark — two views (lock before next harden wave)

| Mode | Question |
|------|----------|
| **A. Fixed-resource** | Same model / tools / time / token budget → better trustworthiness outcome? |
| **B. Cost-normalized frontier** | How much extra resource to cut material failures by X? |

One mode alone can punish overhead (A) or buy a win (B). Both are required to see the trade-off.

## A-F5 (test artifact regeneration)

**Known issue / deferred failure candidate** — not an automatic pre-exam fix on `5d15600`,  
**iff** it does not sit on locked M1.5 PASS/FAIL gates.  
If the 48h reviewer must rely on that check for the claim → either exclude it from claim scope **before** exam, or declare freeze unsuitable. Default: `affects_current_48h_exam: false` until shown otherwise.

## 48h workload identity

Cognitive / research workload, **not** uptime. Across ≥48h expect new evidence, rejected hypotheses, invalidation, recovery, changed decisions, and checkable artifacts — otherwise we only showed the process can fail to terminate for a long time.

## Post-M1.5 mechanism bet (plan only)

```text
Next mechanism candidate (NOT SHOWN / NOT BUILT):
  Mission-Level Runtime Assurance + Bounded Recovery
  Plan: artifacts/hardening/NEXT_MECHANISM_MISSION_ASSURANCE.md
  Benchmark: SAFE_AUTONOMY_BENCHMARK-v1 METRICS_FROZEN
  MCID: SET_BY_VARIANCE_PILOT_v1 (synthetic lock reused)
  T1: REJECT — MIER↓ but completion utility tax (Verifier Tax 2.0)
  Post-T1 diagnostics → SAFE_CONTAINMENT_BUT_LOW_FAULT_SALVAGE
  T2: KEEP — selective bounded recovery on PACK-v2 (FSR=1.0, URR=0, MIER=0)
  C2 contract SELECTIVE_BOUNDED_RECOVERY-v1 FROZEN_CANDIDATE (pin e6dfd08)
  T3: KEEP — live continuation under Groq LIVE_LLM (same prereg / PACK-v3 / C2)
  Experiment freeze SHA: c6523a6 · Live completed SHA: 3ef3f44
  Claim strength: live generalization SHOWN once; independent replication NOT YET;
                  production security NOT SHOWN; Trust Kernel promotion NO
  Attested: no C2/decision-rule edits after unseal (honesty tooling only: 429/pace/TPD)
  Cycle CLOSED — do not retune C2; do not invent PACK-v4; switch to next real task
  Later confidence (optional): NEW prereg + other provider + new sealed holdout + same C2
  Forbidden: proven universal H_TRUST / Trust Kernel / production from this KEEP
  Do not rewrite T1 MCID; do not reopen M1.5; no Y23; T1 REJECT stands for pack v1

Y24 CLOSED (scientific):
  F1 INCONCLUSIVE | F2 REJECT under Y24-AVCT-v1-F2
  Fidelity HEURISTIC_HARNESS_v1
  Adaptive-C advantage: NOT SHOWN / REJECTED under protocol
  Trust Kernel: UNCHANGED — do not rescue Y24 with more N/tuning/PACK-v4

Y25 CAMPAIGN_CLOSED REJECT (ratio≈0.80 vs ≤0.60)
  memory value NOT SHOWN at preregistered strength
  No Y25-F2 / retune / live-LLM rescue
  Y24+Y25: strong cellular features lack evidence → pause self-architecture
  Next: EXTERNAL_REAL_WORK (artifacts/NEXT_EXTERNAL_REAL_WORK.md)
```
