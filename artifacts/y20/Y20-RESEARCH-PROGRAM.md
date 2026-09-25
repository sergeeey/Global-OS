# Y20 Research Program — Preregistered A/B Causal Campaign

**Status:** Binding for Y20 design / prereg (arms **not** started)  
**Not:** M1.5 · Literal 48h · Continual SI · Y19 reopen · Ablation C (deferred)

## Why Y20 exists

Y19 showed a multi-step autonomous research loop in the **bundle**
`strong model + Global OS + infra`. It did **not** prove Global OS architectural
advantage over a strong agent alone. Y20 measures that contribution.

## Terminal mission (same for both arms)

On a **new** statistical-causal synthetic domain (not Boolean dynamics): recover a
limited part of the hidden causal structure and predict interventional outcomes
`do(X=x)` on sealed environments.  
`SUPPORTED` / `REJECTED` / `INCONCLUSIVE` equally valid.

## Design: A/B with equal budget

| Arm | Stack |
|-----|--------|
| **A** | Strong agent + ordinary workspace + scripts (full research freedom) |
| **B** | Same model + Goal Contract + durable research state + falsification loop + autonomous continuation + stop conditions |

Locked equalizers (see `Y20-PREREG.md`):

- same model / provider pin
- same public data bytes (hash)
- same tool surface (filesystem + python)
- same wall-time, token, and tool-call caps
- no compute top-up for the losing arm

**Ablation C** (strong agent + durable checkpoint only) is FUTURE — not part of Y20.

## Operating rules

1. Preregister metrics, budgets, and stop criteria **before** arm execution.
2. Do not peek sealed ground truth (DAG / true interventions) into arm prompts.
3. Operator must not dispatch next-hypothesis choice for either arm.
4. Arms run in isolated directories/worktrees; blind scorer before unblinding.
5. ADR-0009: eval harness / evidence only — no new T0/T1 surfaces.
6. Honest profile > forced GOS win. Equal quality at higher cost is a valid result.

## Stop conditions (campaign level)

- Both arms finished or hit budget wall → score → comparison report
- Critical integrity defect that would invalidate comparison
- Operator authority needed (secrets / out-of-scope capability)

## Hard forbids

- Starting Arm A/B before `phase=PREREG_LOCKED` and public-pack hash locked
- Reopening Y19 H8
- Claiming GOS advantage before `COMPARISON_REPORT`
- Literal 48h / M1.5 / Continual SI claims from Y20 alone
- Unequal budgets after lock

## Handoff files

| File | Purpose |
|------|---------|
| `Y20-PREREG.md` | Locked metrics, budgets, hypotheses |
| `CURRENT_STATE.json` | phase, arm status, hashes |
| `public/` | Observational data + protocol visible to arms |
| `sealed/` | Ground truth — scorer only; not for arm prompts |
| `arms/A/`, `arms/B/` | (future) execution workspaces |
| `COMPARISON_REPORT.md` | (future) after both arms scored |

## Resume

Read this file + `CURRENT_STATE.json` + `Y20-PREREG.md` before any clarifying question.
If `phase=PREREG_LOCKED` and `arms_started=false`, do **not** invent science —
next operator/agent action is to **execute** A/B under the locked prereg (separate stage).
