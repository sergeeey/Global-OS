# Experimental Protocol — GE-STUDY-v1

## 0. Separation of execution classes

| Class | Status in this repo seal | May support claims? |
|-------|--------------------------|---------------------|
| Deterministic behavioral agents | **EXECUTED** (`python -m global_os.evals.goal_engineering.runner`) | Yes, within fidelity |
| Live LLM coding/research/multi-step | **NOT EXECUTED** | No — protocol only below §7 |

Do not merge these classes in prose.

## 1. Design

- **Design:** factorial — Strategy (3) × Domain (3) × Seed (20)  
- **N trials:** 180 per seal  
- **Master seed:** `29072026` (`MASTER_SEED`)  
- **Primary metric:** `oracle_success`  
- **Inferential:** nonparametric bootstrap mean / difference, 90% CI, 2000 resamples  

## 2. Strategies

Constructed in `strategies.py` / `tasks.py`:

1. **S_TRAD** — vague prompt; assertion completion; empty ledger  
2. **S_DETAIL** — numbered steps (intentionally complete on coding; incomplete on research retraction + multi-step verify — models brittle runbooks)  
3. **S_GE** — GoalContract + DoD + EvidenceLedger; SUCCESS only if required criteria have ledger entries matching gates  

## 3. Tasks

| task_id | domain | Oracle gist |
|---------|--------|-------------|
| `coding_sum_range` | coding | Inclusive sum fix + tests green + `lib/other.py` untouched |
| `research_status_owner` | research | Alpha status/owner/region after retracting S3; citations clean |
| `multi_step_pipeline` | multi_step | gather→transform→verify→publish; payload == 20 |

World oracles are hidden from strategy prompts; only the independent evaluator reads them.

## 4. Agents (executed class)

`agents.py` — deterministic policy models:

- Stop / evidence / instruction-following differ by strategy  
- Shared competence: can apply the correct coding patch when attempting it  
- **Not** live LLMs; no provider calls  

## 5. Independent evaluator

`independent_evaluator.py`:

- Must not import strategy builders or agent policy internals for scoring decisions  
- Scores artifacts vs `World.oracle`  
- Emits `oracle_success`, `evidence_fidelity`, `false_claim`, `missed_claim`  

## 6. Metrics

| Metric | Definition |
|--------|------------|
| success | `oracle_success` |
| autonomy | `1 - human_interventions/budget_steps` |
| cost | `cost_tokens` (simulated) |
| latency | `latency_ms` (simulated) |
| evidence fidelity | fraction of ledger checks matching oracle |

## 7. Live-LLM extension (PROTOCOL ONLY — not executed)

When resources allow:

1. Freeze this protocol version and task oracles.  
2. Use one scaffolding (tools, budgets) for all arms; vary **only** the tasking packet.  
3. Models: ≥2 providers; ≥3 seeds/model; pre-register MCID (suggest +5pp oracle_success).  
4. Independent evaluator: separate model family **or** pure machine oracle (preferred).  
5. Cap wall time / tokens identically; record refusals as non-success.  
6. Seal JSON with `execution_class: EXECUTED_LIVE_LLM` and provider digests.  
7. Do **not** copy deterministic H* verdicts into live claims.

## 8. Reproduction

```bash
PYTHONPATH=src python3 -m global_os.evals.goal_engineering.runner
PYTHONPATH=src python3 -m pytest tests/evals/test_goal_engineering_study.py -q
```

Outputs: `artifacts/goal_engineering/results/results.json`, `RESULTS_SEAL.md`.

## 9. Ethics / authority

No external side effects; no secret access; no T0/T1 architecture expansion (eval harness only, ADR-0009).
