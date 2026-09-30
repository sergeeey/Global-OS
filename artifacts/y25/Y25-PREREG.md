# Y25 — Memory Value on Real Failure Incidents

**Status:** `PREREG_LOCKED`  
**Protocol id:** `Y25-MV-v1`  
**Campaign id:** `Y25`  
**Date (UTC):** 2026-09-30  
**Parent closed:** Y24 (`CAMPAIGN_CLOSED`) — H_memory there was **INCONCLUSIVE**, not resolved

## Scientific question

Does durable memory of a previously experienced failure class make the next
**unseen variant** of that class cheaper to diagnose/contain, without inflating
false positives or escaped errors?

```text
first unknown failure (repo R1)
  → diagnose → fix/contain → store experience
then different repo / different code (R2 ≠ R1)
  → unseen variant of same failure_class
Compare: WITHOUT_MEMORY vs WITH_MEMORY
```

This is the cellular “immune memory” idea as an **engineering hypothesis**,
independent of Y24’s adaptive-threshold primary claim (which REJECTed).

## Hypotheses

### H_primary (memory value)

On sealed holdout pairs `(first, unseen_variant)` of the same `failure_class`
with different `repo` / `patch_ref` / `task_id`:

WITH_MEMORY achieves median **pair-cost** on the unseen variant ≤ **0.60×**
the WITHOUT_MEMORY cost on that same unseen variant (or ≤ 0.60× WITH_MEMORY’s
own first-encounter cost — see scoring), **and**:

- false-positive rate not worse than WITHOUT_MEMORY by more than MCID_fp
- escaped-error rate not worse than WITHOUT_MEMORY by more than MCID_escape

### H_null

Memory does not deliver the required cost reduction without FP/escape inflation
→ REJECT (valuable negative).

### H_inconclusive

Underpowered N, pack integrity fail, provider/env block, or isolation breach.

## Arms

| Arm | Definition |
|-----|------------|
| **W0** | WITHOUT_MEMORY — same diagnostic/fix procedure; **no** durable cross-task failure memory |
| **W1** | WITH_MEMORY — identical procedure + durable store of prior failure_class experience from **DEV / first encounters only** (not holdout labels) |

Both arms use the same budgets, tool gateway, model adapter path, and cost ledger.
No Trust Kernel edits. No silent network fallback.

## Unit of analysis

**Incident pair** for a failure class X:

1. `memory_role=first` — first unknown failure (diagnose/fix/store)
2. `memory_role=unseen_variant` — different repository or substantially different
   code path; same curated `failure_class`; **not** the same patch/case

Hard forbid: scoring “memory” on the same case twice.

## Corpus (OSS real incidents)

- Source: public OSS bug/security fix incidents (commits/PRs) with clear
  failure_class labels assigned **a priori**
- Minimum: **≥12 pairs** (24 incidents) after seal; target ≥16 pairs
- Holdout: ≥50% of pairs sealed unseen before arm runs
- DEV: used only to seed W1 memory from first encounters (and calibrate tooling)

## Metrics (ledger, both arms)

| Metric | Weight in `pair_cost` |
|--------|----------------------|
| `time_to_diagnosis_s` | 1.0 |
| `tool_calls` | 50.0 |
| `llm_cost_tokens` | 1.0 |
| `human_interventions` | 5000.0 |
| `verification_calls` | 100.0 |
| `latency_ms` | 0.001 |
| `recovery_overhead_seconds` | 10.0 |

Also recorded (not in cost formula unless listed): `false_positive`, `escaped_error`,
`task_contained`.

`pair_cost` uses the same linear form as Y24 cost accounting (locked in
`Y25-COST-ACCOUNTING.md`) so campaigns remain comparable without merging claims.

## MCID / gates (locked before unseal)

| Symbol | Value | Role |
|--------|------:|------|
| `MEMORY_COST_RATIO_MAX` | 0.60 | W1 unseen cost / reference ≤ this |
| `MCID_fp` | 0.05 | FP rate W1 ≤ W0 + MCID |
| `MCID_escape` | 0.05 | escape rate W1 ≤ W0 + MCID |
| `COST_BUDGET_PARITY` | same arm budgets | no free compute |

**Reference for cost ratio (primary):** W1 unseen median cost / W0 unseen median cost  
**Secondary report:** W1 unseen / W1 first (within-arm learning curve)

## Decision

- **KEEP** if H_primary gates pass on sealed holdout pairs (N≥12 pairs scored)
- **REJECT** if powered and gates fail
- **INCONCLUSIVE** if underpowered / env / integrity

KEEP under heuristic fidelity ≠ live-LLM proof; ≠ Trust Kernel promote.

## Isolation

W1 memory implementers must not access sealed holdout labels/outcomes before
execution unseal. Attestation required (`Y25-ISOLATION.md`).

## Forbidden

- reopen Y24 for threshold fishing / C tuning / PACK-v4
- treat Y24 H_memory INCONCLUSIVE as SUPPORT
- same-case “memory” (not unseen variant)
- select holdout pairs using arm outcomes
- post-hoc failure_class relabel after unseal
- Trust Kernel / C2 edits for Y25
- production / universal memory claims from one KEEP
- architecture rewrite because Y24 rejected

## Relationship to Y24

Y24 closed: Adaptive-C advantage **NOT SHOWN** under heuristic protocol.
Y25 does **not** retry Y24 primary. It tests memory value alone on real incidents.
