# Goal Engineering Study (GE-STUDY-v1)

Independent scientific-engineering investigation: does **Goal Engineering** (GoalContract + Definition of Done + EvidenceLedger) improve autonomous agent outcomes versus traditional vague prompts and detailed procedural instructions?

## DoD map

| Definition of Done item | Artifact |
|-------------------------|----------|
| Systematic source review | `LITERATURE_REVIEW.md`, `sources.json` |
| Falsifiable hypotheses | `HYPOTHESES.md` |
| ≥3 tasking strategies | `S_TRAD`, `S_DETAIL`, `S_GE` in code + docs |
| Reproducible experimental suite | `PROTOCOL.md`, `src/global_os/evals/goal_engineering/` |
| Metrics: success, autonomy, cost, latency, evidence fidelity | `RESULTS.md`, `results/results.json` |
| Independent evaluator | `independent_evaluator.py` |
| Uncertainty + limitations | `RESULTS.md` |
| GE Spec v1.0 from confirmed results | `SPEC_v1.0.md` |

## Execute

```bash
PYTHONPATH=src python3 -m global_os.evals.goal_engineering.runner
PYTHONPATH=src python3 -m pytest tests/evals/test_goal_engineering_study.py -q
```

## Critical boundary

- **EXECUTED:** deterministic behavioral agents (180 trials).  
- **NOT EXECUTED:** live LLM A/B/C — protocol in `PROTOCOL.md` §7 only.  
- Do not treat deterministic CONFIRMED hypotheses as production LLM proof.
