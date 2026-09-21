# EVALS.md

## Survival Benchmark (GoalIntegritySurvival)

Long task 24–48h with injections: process kill, model swap, API outage, false tool success, source invalidation, contradictory evidence, malicious document, human rejection, constraint change, budget reduction, duplicate action, corrupted state, slow dependency.

Primary metric: **GoalIntegritySurvival**.

## Organizational Topology Benchmark (H-ORG-001)

Compare: single agent · flat swarm · manager→workers · recursive hierarchy · hierarchy+verification · dynamically compiled org.

Task sizes: 10 / 30 / 100 / 300 / 1000 subtasks; varied dependency structures.

Metrics: goal success, cost, latency, duplicate work, coordination overhead, information loss, escaped errors, manager bottleneck, recovery rate, evidence quality, org depth, reorganization frequency.

### Kill criteria

Recursive architecture is not default if it fails to raise success, increases error propagation, burns gains on management cost, loses evidence in summaries, loses to manager-worker, or loses to single strong agent on cost/quality.

## Baseline discipline

Every complexity vs **Strong Single Agent** (and sometimes scripted workflow).

## Experiment format

id, hypothesis, baseline, intervention, dataset/tasks, metrics, success_threshold, kill_threshold, budget, preregistered_at, results, verdict, reopen_condition.

## Primary project score

$$
AutonomyEfficiency = \frac{VerifiedUsefulWork}{HumanAttention \times UnverifiedTrust \times Cost}
$$
