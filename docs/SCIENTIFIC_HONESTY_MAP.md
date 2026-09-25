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

M1.5 claim fork (2026-09-25) — see artifacts/hardening/M15_CLAIM_FORK.md
  5d15600 embedded workload = deterministic durability harness (sum 1..20 …)
  → A: narrow “48h research-runtime integrity” ONLY if someone runs 48h on it
  → B (CHOSEN): LH-COGNITIVE-v1 external object → new freeze → then 48h
  Running/finished Windows preflight on 5d15600 = DURABILITY_ENV evidence
  Do NOT start wall_48h on 5d15600 for cognitive-real M1.5 claim

M1.5 (Gate A — cognitive path)
  Long-horizon integrity on frozen REAL research workload ≥48h?
  → TO TEST after LH-COGNITIVE freeze (not on 5d15600 sum-harness)

Post-M1.5
  Does a trust layer reduce predefined material integrity failures
  enough to justify operational cost?
  → CORE NEXT HYPOTHESIS (H_TRUST)
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
Trust / long-horizon amplification: TO TEST  (M1.5 then H_TRUST)
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

## H_TRUST (draft — freeze metrics before Trust Kernel work)

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
