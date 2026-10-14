# Results — GE-STUDY-v1

> **POST-HOC AUDIT:** See `POST_HOC_AUDIT.md`. Original H1–H5 **CONFIRMED** labels are demoted to **MECHANISM_DEMO_NOT_CAUSAL**. Immutable seal: `results/v1_immutable/`. Corrected appendix: `results/v1_1_post_audit/`.

## Execution boundary (read first)

| What | Status |
|------|--------|
| Deterministic behavioral suite (180 trials, 3 strategies) | **EXECUTED** — frozen in `results/v1_immutable/` |
| Post-audit 4-arm appendix (+ `S_DETAIL_VERIFIED`) | **EXECUTED** — `results/v1_1_post_audit/` |
| Live LLM comparative trials | **NOT EXECUTED** — see PROTOCOL §7 |
| Causal GE superiority over good runbooks | **NOT SHOWN** |
| Production / universal GE superiority | **NOT CLAIMED** |

Machine seal (immutable): `results/v1_immutable/RESULTS_SEAL.md`.

## Aggregate (n=60 trials / strategy)

| Strategy | oracle_success | false_claim | evidence_fidelity | cost_tokens | latency_ms |
|----------|----------------|-------------|-------------------|-------------|------------|
| S_TRAD | 0.300 [0.200, 0.400] | 0.700 | 0.000 | 190.3 | 100.7 |
| S_DETAIL | 0.333 [0.233, 0.433] | 0.667 | 0.000 | 186.7 | 101.7 |
| S_GE | 1.000 [1.000, 1.000] | 0.000 | 1.000 | 231.7 | 125.0 |

90% bootstrap CIs on means (overall success shown).

### Contrasts (S_GE − baseline)

| Contrast | estimate | 90% CI |
|----------|----------|--------|
| oracle_success − TRAD | +0.700 | [0.600, 0.783] |
| oracle_success − DETAIL | +0.667 | [0.567, 0.767] |
| false_claim − TRAD | −0.700 | [−0.800, −0.600] |
| evidence_fidelity − TRAD | +1.000 | [1.000, 1.000] |
| cost_tokens − TRAD | +41.3 | [26.2, 56.4] |
| latency_ms − TRAD | +24.3 | [18.8, 29.6] |

## Hypothesis verdicts (deterministic class only)

| ID | Verdict | Notes |
|----|---------|-------|
| H1 GE > TRAD success | **CONFIRMED** | CI excludes 0 |
| H2 GE > DETAIL success | **CONFIRMED** | Driven by research + multi_step |
| H3 GE < TRAD false_claim | **CONFIRMED** | |
| H4 GE > baselines evidence | **CONFIRMED** | DETAIL informal ledger scores 0 |
| H5 GE cost/latency tax | **CONFIRMED** | ~+22% tokens, ~+24% latency vs TRAD |

## Conditional winners (oracle_success)

| Domain | Winner | Interpretation |
|--------|--------|----------------|
| coding | `S_DETAIL=S_GE` (tie @ 1.0) | Complete steps suffice for outcome; **GE alone** has evidence_fidelity=1.0 |
| research | `S_GE` | TRAD/DETAIL keep retracted/rumor status → false claims |
| multi_step | `S_GE` | DETAIL omits verify → systematic false publish; TRAD verifies only half of seeds |

## When GE outperforms / ties / loses (this fidelity)

**Outperforms**

- Incomplete or stale procedures (missing retraction / verify)  
- High false-pass cost (liability) — GE false_claim = 0 here  
- Need for auditable evidence, not only outcome

**Ties on outcome**

- Simple coding with a complete, correct runbook (DETAIL = GE on success)

**No domain loss on oracle_success in this suite**

- GE did not underperform DETAIL/TRAD on success in any domain here  
- GE **did** pay a cost/latency tax (H5)  
- GE can block (`claimed_blocked`) when ledger incomplete — preferable to false SUCCESS

**Not measured (must not invent)**

- Live LLM variance, prompt injection, tool outages  
- Well-authored DETAIL that includes verify + retractions (would likely close the gap)  
- Whether humans prefer GE authoring cost vs writing steps

## Statistical uncertainty

- Bootstrap 90% CIs; n=60 per strategy aggregate; n=20 per domain×strategy  
- No multiple-comparison correction across H1–H5 (correlated metrics)  
- Behavioral agents reduce model noise → CIs are **optimistic vs live LLM**  
- DETAIL steps are adversarially incomplete on 2/3 tasks by design — estimates GE advantage vs **brittle** procedures, not vs ideal SOPs

## Independent evaluator

Module `independent_evaluator.py`; details embed `"evaluator": "independent_oracle_v1"`.  
Does not call agent policies. Same process, separate code path (GOS-I10: not same-model self-certification of success).

## Limitations

1. Deterministic agents ≠ foundation models  
2. Three tasks only  
3. Simulated tokens/latency  
4. DETAIL arm models brittle instructions on research/multi_step  
5. Autonomy metric nearly saturated (no HITL pressure in this suite)  
6. Live-LLM protocol written but **not run**
