# POST_HOC_AUDIT — GE-STUDY-v1 (PR #47)

**Status:** Binding honesty correction  
**Date:** 2026-10-14  
**Immutable seal:** `results/v1_immutable/` (SHA-256 of `results.json` at freeze: see `IMMUTABLE.md`)  
**Verdict on research claim:** **REQUIRES_REVISION** — useful engineering harness, **not** independent causal proof of GE superiority

## 1. Audit findings (accepted)

| Check | Finding | Impact |
|-------|---------|--------|
| Oracle independence | Agents read `world.oracle[...]` in v1 `agents.py` | Experimental isolation **broken** in sealed run |
| Comparison fairness | `S_DETAIL` intentionally omitted verify / S5 | GE advantage vs brittle SOP **inflated** |
| Statistical independence | 180 episodes = 3 tasks × 3 strategies × 20 seeds | CIs ≠ uncertainty over new tasks |
| Bootstrap seeds | `hash()` used for CI seeds | Intervals may differ across Python processes |
| Cost / latency | Simulated counters | No measured LLM overhead |
| Live LLM | Not executed | No real-mission efficacy claim |

These defects do **not** imply the printed means `1.00 / 0.30 / 0.33` are arithmetic errors. They accurately describe the **scripted simulator**. They must **not** be read as independent causal confirmation that Goal Engineering improves equally capable real agents.

## 2. Claim demotion (mandatory)

| Original label (v1 seal) | Post-hoc label |
|--------------------------|----------------|
| H1–H5 **CONFIRMED** | **MECHANISM_DEMO_NOT_CAUSAL** |
| “GE outperforms baselines” | “Scripted GE policy beats scripted brittle/vague policies on 3 hand-crafted worlds” |
| Spec v1.0 “confirmed results” | Engineering construct + **mechanism** evidence only; causal GE advantage **NOT SHOWN** |

```text
simulator_success ≠ causal_advantage_for_live_agents
pretty_CIs_on_3_tasks ≠ generalization_uncertainty
```

## 3. What remains useful

GE-STUDY-v1 is a valid **contract/evidence gate test bench**:

- Exercises GoalContract + DoD + EvidenceLedger shapes  
- Surfaces false-claim failure modes of assertion-based stop  
- Documents a live-LLM protocol (still NOT_EXECUTED)

It is **not** a substitute for: large real Operator missions, measured $/latency, or equally tooled live A/B/C.

## 4. Remediation executed in this PR (post-audit)

Kept: original seal bytes under `results/v1_immutable/`.

Added / fixed:

1. **Oracle isolation** — agents receive `AgentView`; `world.oracle` access raises; no oracle reads in policy code.  
2. **Stable stats** — FNV seeds (no `hash()`); **paired** bootstrap on shared `(seed, task_id)` cells.  
3. **Control arm `S_DETAIL_VERIFIED`** — complete runbook (tests gate / S5+retractions / verify-before-publish).  
4. **Appendix seal** — `results/v1_1_post_audit/` (mechanism demo with fairer DETAIL control; still not live LLM).

## 5. What still does NOT count as proof

Even after remediation:

- Agents remain deterministic behavioral models  
- Task diversity remains n_tasks = 3  
- Cost/latency remain simulated  
- Live LLM A/B/C remains **PROTOCOL_ONLY**

Causal GE value over a **good** alternative organization of work requires live trials with identical tools, budgets, and independent evaluation on **held-out** tasks.

## 6. Pre-production stance (unchanged)

Global OS pre-production criterion remains: real large task, working Operator path, verified outcomes, measured cost and time.  
GE-STUDY numbers must not replace that criterion.
