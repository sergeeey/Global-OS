# M-EXT4 — Post-hoc independent scientific audit

**Status:** `POST_HOC_AUDIT_LOCKED`  
**Date (UTC):** 2026-10-02  
**Audited commit:** `43c5ba4` (`DECISION.md` and co-located deliverables)  
**Rule:** This file does **not** rewrite agent artifacts. Original `DECISION.md` remains historical.

---

## Headline (corrected accumulated claim)

```text
M-EXT4
exam outcome: SUCCESSFUL SCIENTIFIC TRIAGE
broad novelty: NOT NOVEL
specific init-based novelty: UNRESOLVED
empirical Mpemba effect: NOT TESTED
original formulation: PARTLY ILL-POSED
```

### Split stories

| Story | Verdict |
|-------|---------|
| Did Global OS autonomously triage a scientific hypothesis? | **YES** — successful exam |
| Is the broad Mpemba-in-NN-training + Fisher claim novel as stated? | **NOT NOVEL** (Liu & Hu 2025 prior art) |
| Is initialization-induced Mpemba at fixed LR novel? | **UNRESOLVED** (not settled by M-EXT4) |
| Does the empirical effect exist? | **NOT TESTED** (pilot/confirmatory not run) |
| Was SOURCE_HYPOTHESIS operationally clean? | **PARTLY ILL-POSED** |

---

## What the agent did well (preserve)

1. Found Liu & Hu (arXiv:2507.04206) and used it as a hard novelty gate.  
2. Separated formalization problems (P1–P5) instead of silently “fixing” the hypothesis.  
3. Enumerated competing explanations and locked a prereg *before* claiming empirical results.  
4. Chose an allowed terminal (`NOT_NOVEL_IN_CLAIMED_FORM` / `ILL_POSED`) rather than inventing SUPPORTED.  
5. Did not edit Global OS architecture; did not edit `SOURCE_HYPOTHESIS.md`.

These support: **exam = SUCCESSFUL SCIENTIFIC TRIAGE**.

---

## Findings requiring errata

### F1 — Over-strong novelty truncation of the narrow claim

**Agent claim:** residual init-based novelty is “insufficient” / folded into broad NOT_NOVEL.  
**Audit:** Broad claim overlap with Liu & Hu is strong. The **narrow** claim (hot/cold via **initialization variance at fixed LR**, not LR-schedule temperature) is a **different construction**. M-EXT4 did **not** run a dedicated novelty adjudication that closes that residual.  
**Correct status:** `specific init-based novelty: UNRESOLVED` (not “disproven”; not “established”).

### F2 — Empirical effect left UNKNOWN (must stay visible)

Pilot/confirmatory were skipped after triage. That is allowed for the **exam** outcome, but external science headlines must not read as “Mpemba absent.”  
**Correct status:** `empirical Mpemba effect: NOT TESTED`.

### F3 — Fisher–Rao / FIM argument contains overclaim

Agent treats “Fisher–Rao requires FIM⁻¹; FIM singular ⇒ infeasible” as decisive.  
**Audit nuances:**

- Predictive KL between output distributions is **not** the same as a Fisher–Rao geodesic on parameters.  
- Singularity of the empirical FIM does not by itself prove every Fisher-geometry *mechanism claim* is meaningless; it constrains **which** operationalizations are valid.  
- Saying the user’s Fisher link is ill-posed / under-specified is fair; saying Fisher geometry is globally infeasible as an explanatory *hypothesis class* is stronger than the math shown.

**Correct status:** Fisher mechanism claim in SOURCE is **under-specified / partly ill-posed**; agent’s absolute “infeasible” wording is **overclaim** → see `ERRATA.md`.

### F4 — Statistical decision rule internally inconsistent

Prereg / reproducibility pack: primary SUPPORTED at **≥14/20** wins under one-sided binomial H0: p=0.5, α=0.05.

Exact values:

```text
P(X ≥ 14 | Bin(20, 0.5)) ≈ 0.0577  (> 0.05)
P(X ≥ 15 | Bin(20, 0.5)) ≈ 0.0207  (< 0.05)
```

So **14/20 does not meet p<0.05**; **15/20 does**. The locked prereg’s numeric threshold and its stated p-value do not match.  
**Correct status:** decision rule needs repair in any **new** prereg (M-EXT5); do not silently patch M-EXT4 prereg post-hoc for optics.

### F5 — “Confirmatory ready” ≠ runnable confirmatory

`REPRODUCIBILITY_PACK.md` documents `python3 mpemba_experiment.py --confirmatory`.  
Actual code path:

```text
--confirmatory → print ERROR and sys.exit(1)
```

No sealed-holdout loader / confirmatory loop is implemented. Pilot path exists; confirmatory is **not** replication-ready as advertised.  
**Correct status:** code = pilot-oriented scaffold; confirmatory implementation **incomplete**.

### F6 — Uncalibrated probability language

Agent reports `P(init-based Mpemba | …) ≈ 0.6` as epistemic humility.  
**Audit:** Without a calibrated uncertainty protocol, this is **not** a scientific probability. Treat as informal prose only; do not propagate into capability/maturity claims.

### F7 — Ledger field drift (minor)

`MISSION_LEDGER.json` marks phases E/H DONE but still has `"prereg_locked": false` and `"arms_or_holdout_sealed": false` while `SEALED_HOLDOUT.json` exists. Historical inconsistency; do not rewrite silently for score — noted here.

---

## Process lesson (Global OS)

Real bottleneck exposed:

```text
not: “can the system investigate at all?”
but: “can it adequately verify its own scientific terminal claim?”
```

**Process gate for future science missions (no new ScienceKernel):**

```text
agent terminal decision
        ↓
independent post-hoc scientific audit
        ↓
only then external headline / merge narrative
```

This continues the Verification Plane without architecture shopping.

---

## Implications

1. **Keep M-EXT4 immutable** — original decision stands as agent history.  
2. **Publish this audit + ERRATA** beside it; correct accumulated claims in honesty map / RUN_STATE.  
3. **Do not** reopen M-EXT4 to “get SUPPORTED.”  
4. **Open M-EXT5** for the residual scientific question (init-based effect ⊥ Fisher mechanism) with mechanical gates before any pilot.

---

## Audit disposition

| Item | Disposition |
|------|-------------|
| M-EXT4 exam success | **AFFIRM** |
| Broad NOT_NOVEL | **AFFIRM** (with Liu & Hu as prior art) |
| Narrow novelty closed | **REJECT agent closure** → UNRESOLVED |
| Empirical absence | **REJECT any such reading** → NOT TESTED |
| Merge readiness | **OK after this audit layer is on the branch** |
