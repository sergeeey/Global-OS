# M-EXT3 Preregistration — Locked before arm execution

**Protocol:** `M-EXT3-GSA-v1`  
**Exam id:** `M-EXT3-GSA`  
**Arms started:** `false` until task pin + this prereg boundary SHA recorded  
**Machine copy:** `M-EXT3-PREREG.json`

## Hypothesis

> **H_GSA:** On a pinned open OSS incident (M-EXT1 class), under equal model/tool/budget
> caps, the Global OS assembled workflow (Arm B) reaches a hard-gated
> `ROOT_CAUSE_CONFIRMED` (or strictly better honest terminal) more often / more
> completely than a strong single-agent baseline (Arm A).

Falsifiable. One task cannot prove universality.

## Equal budgets (hard)

| Resource | Cap (each arm) |
|----------|----------------|
| Wall investigation | **6 hours** |
| Scripted repro/patch runs | **40** |
| Manual hypothesis pivots | **8** |
| Provider LLM USD (if used) | **$5** |
| Global OS code edits for optics | **0** |
| Model pin | **identical A/B** |
| Public task pack | **identical SHA** |

Exhaust → arm must stop with honest terminal; no “чуть-чуть ещё” after envelope.

## Hard gate (same shape as M-EXT1)

An arm may claim `ROOT_CAUSE_CONFIRMED` only if **all** hold:

1. Stable repro on pinned SHA  
2. Mechanism + ≥1 disconfirming test for rejected alternatives  
3. Local patch eliminates the failure on repro  
4. Regression **fails before** patch and **passes after**

Else: `REJECTED` or `INCONCLUSIVE` (honest).

## Primary decision rule (immutable)

Let `HG(arm) = 1` iff hard gate fully met and terminal is `ROOT_CAUSE_CONFIRMED`, else `0`.

| HG(A) | HG(B) | Primary verdict |
|-------|-------|-----------------|
| 0 | 1 | **B_ADVANTAGE** |
| 1 | 0 | **A_ADVANTAGE** |
| 1 | 1 | **TIE** (both delivered; no primary advantage) |
| 0 | 0 | **TIE_NULL** on primary; secondaries may note process differences but **cannot** claim B_ADVANTAGE |

`INCONCLUSIVE` if: task selection failed post-hoc, budget asymmetry, cross-arm leakage,
or protocol integrity break.

## Secondary (cannot override primary to manufacture B_ADVANTAGE)

- Counterevidence discipline (rejected hypotheses with tests)
- False root-cause claims withdrawn vs stuck
- Human interventions count
- Budget remaining at honest stop
- Artifact completeness (repro/logs/patch/regression pack)

## Isolation

- Neither arm may read the other’s workdir / ledger / patch
- Score only after both arms frozen
- Prefer generator/task-pinner ≠ arm runners; record caveat if same lineage

## Immutable priors

- M-EXT1: IMMUTABLE — do not polish urllib3 for this exam’s optics  
- M-EXT2: CLOSED — no F2 label-fish as substitute  
- Y24/Y25/T3: not evidence for H_GSA  
- Architecture shopping from outcome: forbidden  

## Terminal artifacts required

Per arm: GOAL snapshot, competing explanations, repro+logs, terminal verdict,
budget ledger, patch+regression if claiming ROOT_CAUSE_CONFIRMED.

Exam-level: `COMPARISON_REPORT.md`, `SCORE_RAW.json`, `CLAIMS.md`, `M_EXT3_CLOSED.*`.
