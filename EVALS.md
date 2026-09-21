# EVALS.md

## Survival Benchmark (GoalIntegritySurvival)

Only **runtime_injected** scenarios count toward GoalIntegritySurvival. Stub catalog scenarios are informational (`stub_completion_rate`).

Primary metric: **GoalIntegritySurvival** over runtime_injected set.

## Organizational Topology Benchmark (H-ORG-001)

Compare: single agent · flat swarm · manager→workers · recursive hierarchy · hierarchy+verification · dynamically compiled org.

### Kill criteria

Recursive architecture is not default if it fails to raise success, increases error propagation, burns gains on management cost, loses evidence in summaries, loses to manager-worker, or loses to single strong agent on cost/quality.

## Environment Benchmark (H-ENV-001)

> After minimally sufficient instructions, improving task **environment** yields larger marginal gain than further prompt elongation.

Compare same model/task/prompt across environments:

```text
A no tools
B browser
C browser + sandbox
D browser + sandbox + evidence
E full Global OS environment
```

Separately: same environment, different prompts.

**Do not** treat “80% environment / 20% prompt” as a fact — it is a rhetorical claim to be tested.

Harness status: `global_os.evals.environment` runs **synthetic_deterministic** sweeps; verdict stays `INCONCLUSIVE_NEEDS_REAL_MODEL` until frontier-model evidence is recorded.

## Reasoning Budget (H-RSN-001)

Dynamic reasoning allocation improves quality/cost vs fixed-high effort.  
Constraint: ReasoningBudget ≠ VerificationRequirement (GOS-I23).

## Evaluator Calibration (H-EVAL-001)

Calibrated evaluator stack (deterministic checks + judge calibration + bias probes) reduces escaped errors vs raw LLM judge.  
Constraint: judge cannot validate itself (GOS-I24). No magic κ threshold.

## Structured Context (H-CTX-001)

Typed retrieval from state/evidence/memory beats repeated conversation compaction on long-horizon state integrity.

## Baseline discipline

Every complexity vs **Strong Single Agent** (and sometimes scripted workflow).

## Experiment format

id, hypothesis, baseline, intervention, dataset/tasks, metrics, success_threshold, kill_threshold, budget, preregistered_at, results, verdict, reopen_condition.

## Primary project score

$$
AutonomyEfficiency = \frac{VerifiedUsefulWork}{HumanAttention \times UnverifiedTrust \times Cost}
$$
