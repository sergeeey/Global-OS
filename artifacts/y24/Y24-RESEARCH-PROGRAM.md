# Y24 Research Program — Adaptive Verifier Complexity Threshold

**Status:** Binding for design / prereg (arms **not** started)  
**Protocol:** `Y24-AVCT-v1`  
**Naming note:** Informal brief called this “Y19”. Legacy `artifacts/y19/` is
**FROZEN** (NK Boolean transient science). This campaign is **Y24**. Do not reopen
Y19 H8 / feature-mining. Do not call this Y23 (explicitly forbidden).

**Not:** Trust Kernel promote · T0/T1 surface · T3 overturn · production security ·
Continual SI · mathematical query-complexity theorem

## Why Y24 exists

Two idea sources, one measurable question:

```text
Quantum-school: find the regime/headroom where a complex mechanism beats a
                strong simple baseline — do not ask "is complex good?".
Cell/immunity:  a verifier must catch dangerous work without attacking benign
                (autoimmune) work; memory should make repeat failure classes cheaper.
```

Scientific question (primary):

> **Is there a measurable task-complexity threshold above which an adaptive
> verifier with benign negative-selection calibration and memory of prior
> failures yields fewer material escapes than a strong simple verifier, at
> comparable cost and false-block rate?**

Secondary (immune memory):

> **After encountering failure class X, an unseen variant of the same class
> should be detected cheaper without raising false positives.**

## What Global OS must do (dogfood)

```text
Goal Contract
→ competing hypotheses
→ preregistration (LOCKED)
→ data collection / pack seal
→ strong cost-matched baseline
→ sealed holdout
→ experiment
→ counterevidence
→ KEEP / REJECT / INCONCLUSIVE
```

Global OS investigates the answer. Expected direction is **not** preregistered as truth.
`C nowhere pays off` is a valid scientific outcome.

## Competing systems (equal budget)

| Arm | Definition |
|-----|------------|
| **A** | Strong simple verifier (deterministic rules + fixed heuristics; no failure memory; no adaptive escalation) |
| **B** | LLM verifier without durable failure memory (stateless / session-only judgment) |
| **C** | Adaptive verifier: benign calibration (negative selection) + memory of previous failures + bounded escalation |

Budgets must be cost-matched (see `Y24-PREREG.md`). Losing arm must not receive extra compute.

## Task material (real, not toys)

Open-source repository change tasks, labeled before unseal:

```text
benign_safe              ordinary safe changes
benign_suspicious        safe but looks suspicious (critical for autoimmune control)
bugfix_security         real bug/security fixes
dangerous_effect         changes with potentially dangerous effect
```

A substantial share of **benign** tasks must look suspicious. Otherwise C can be
tuned to block everything and fake a win.

Complexity strata (assigned before unseal; sealed rubric):

```text
LOW | MEDIUM | HIGH
```

Primary analysis is **by stratum**, not only pooled accuracy.

## Explicit non-uses of prior work

```text
✗ T3 KEEP is NOT evidence for Y24
✗ SELECTIVE_BOUNDED_RECOVERY-v1 / Trust Kernel must NOT be edited for Y24 win
✗ Y19–Y22 synthetic outcomes do not transfer as Y24 proof
✗ Do not invent PACK-v4 / retune C2 as Y24 setup
```

Y24 is a **new** preregistered mission. Mechanism code for arms A/B/C lives in
eval harness only until KEEP + independent review justify any promotion proposal
(promotion still requires separate ADR — not automatic).

## Future (not Y24)

**Y25** (optional later): empirical verification-budget frontier —

> Is there a lower empirical bound on verification budget below which one cannot
> jointly hold low material-escape rate and low false-block rate?

Do **not** start Y25 until Y24 reaches a terminal scientific result.

## Operating rules

1. Lock prereg + metrics + KEEP/REJECT/INCONCLUSIVE **before** arm execution and before holdout unseal.
2. Seal unseen holdout pack before SHA freeze; do not retune arms after viewing holdout.
3. ADR-0009: eval harness / evidence / honesty only — no new T0/T1 surfaces.
4. Honest profile > forced adaptive win.
5. Dogfood: observe→propose→branch→test→verify→**request merge** (no autonomous T0/T1 merge).

## Handoff files

| File | Purpose |
|------|---------|
| `Y24-RESEARCH-PROGRAM.md` | This contract |
| `Y24-PREREG.md` / `.json` | Locked metrics, arms, budgets, stop rules |
| `CURRENT_STATE.json` | phase machine |
| `public/` | Visible task protocol + benign calibration notes (no holdout labels) |
| `sealed/` | Holdout labels / danger ground truth — scorer only |
| `arms/A|B|C/` | Future execution workspaces |
| `COMPARISON_REPORT.md` | Future, after scoring |
| `Y24_DECISION.md` | Future terminal KEEP/REJECT/INCONCLUSIVE |

## Resume

If `phase=PREREG_LOCKED` and `arms_started=false`: **do not invent results**.
Next stage after this lock: build sealed task pack + harness stubs under prereg
(still no arm execution until pack freeze + SHA freeze).
