# M-EXT4 — ERRATA (post-hoc)

**Status:** `ERRATA_LOCKED`  
**Applies to:** agent terminal package at commit `43c5ba4`  
**Does not modify:** `DECISION.md`, `PREREG.md`, `SOURCE_HYPOTHESIS.md`, sealed holdout, or experiment code history.

Readers of M-EXT4 must apply these corrections when citing the campaign externally.

---

## E1 — Novelty scope

| Location | Original implication | Correction |
|----------|---------------------|------------|
| `DECISION.md` executive / §1.2 | Residual init-based novelty insufficient; folded under NOT_NOVEL | Broad claim: **NOT NOVEL**. Init-based fixed-LR construction: **UNRESOLVED** (not empirically or bibliographically closed). |

## E2 — Empirical status

| Location | Original risk | Correction |
|----------|---------------|------------|
| Terminal without pilot | May be misread as “effect absent” | **Empirical Mpemba effect: NOT TESTED.** |

## E3 — Fisher–Rao / FIM wording

| Location | Original | Correction |
|----------|----------|------------|
| `DECISION.md` P5 / §4; `COUNTEREVIDENCE.md` | Fisher–Rao “infeasible” because FIM⁻¹ singular | User’s Fisher link is **under-specified**. Predictive KL ≠ parameter Fisher–Rao geodesic. Singularity constrains operationalization; it does **not** alone refute every Fisher-*mechanism* hypothesis class. Absolute “infeasible” is **overclaim**. |

## E4 — Binomial threshold

| Location | Original | Correction |
|----------|----------|------------|
| `PREREG.md` §7–8; `REPRODUCIBILITY_PACK.md` | ≥14/20 wins ⇒ p<0.05 | For Bin(20, 0.5) one-sided: **P(X≥14)≈0.0577** (fails α=0.05); **P(X≥15)≈0.0207**. Do **not** use 14/20 as α=0.05 threshold in future protocols without a different test. Fix only via **new** prereg (M-EXT5). |

## E5 — Confirmatory readiness

| Location | Original | Correction |
|----------|----------|------------|
| `REPRODUCIBILITY_PACK.md`; STATUS “code ready” | Implies `--confirmatory` runs the sealed experiment | `mpemba_experiment.py --confirmatory` **exits with ERROR**; no confirmatory runner. Pilot scaffold only. |

## E6 — Probability ≈0.6

| Location | Original | Correction |
|----------|----------|------------|
| `DECISION.md`; `COUNTEREVIDENCE.md` | `P(…)≈0.6` | Informal uncertainty prose **only**. Not a calibrated scientific probability. Do not cite as evidence. |

## E7 — Ledger flags

| Location | Original | Correction |
|----------|----------|------------|
| `MISSION_LEDGER.json` | `prereg_locked: false`, `arms_or_holdout_sealed: false` while Phase E DONE + seal file present | Treat as bookkeeping drift. Seal file hash remains as recorded in `PREREG.md`. |

---

## Citation template (post-errata)

> Under M-EXT4 (`M-EXT4-MPEMBA-v1`), an autonomous agent produced terminal
> `NOT_NOVEL_IN_CLAIMED_FORM` + `ILL_POSED`. Independent post-hoc audit affirms
> successful scientific triage and broad prior art (Liu & Hu 2025), but records
> init-based novelty as **UNRESOLVED**, empirical effect as **NOT TESTED**, and
> listed technical errata (statistics, confirmatory code, Fisher wording, P≈0.6).
> See `POST_HOC_AUDIT.md` and this ERRATA.
