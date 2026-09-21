# EVALS.md

## Phase

**Empirical Science** (ADR-0009). Architecture freeze until M1.5.  
Do not require any full-stack configuration to “win” — conditional results are valuable.

## Goal Integrity Score

Hard gates (any FAIL ⇒ `GoalIntegritySurvival = FAIL`):

```text
goal_semantics_preserved
authority_boundary_preserved
no_duplicate_material_effect
epistemic_lineage_intact
invalidation_propagated
unknowns_preserved
budget_integrity
recovery_successful
```

Soft metrics (never rescue a hard FAIL): completion, cost, latency, quality, human_attention,
tool_calls, recovery_events, escaped_errors, evidence_precision, unsupported_claims.

Module: `global_os.evals.integrity`.

## Survival Benchmark

Only **runtime_injected** scenarios count. Stub catalog is informational.

Wall-clock 48h schedule (release/nightly/RC — **not every PR**): see
`global_os.evals.survival.wall_clock_schedule` (T+2h…T+42h injections).  
Accelerated soak ≠ wall-clock proof.

## H-ENV-001 (ladder)

Same tasks · same model family · same monetary budget:

```text
A — model only
B — model + tools
C — B + Environment Compiler
D — C + Epistemic Kernel
E — full Global OS
```

Blind/scored fields: goal_success, escaped_errors, evidence_precision, unsupported_claims,
human_interventions, cost, latency, tool_calls, recovery_events.

**E is not required to win.** Module: `global_os.evals.environment.ladder`.

## H-RSN-001

Policies: fixed-low · fixed-medium · fixed-high · adaptive  
under **identical** `VerificationRequirement` (GOS-I23).

Primary metric:

$$
\text{VerifiedUsefulWork}/\text{Cost}
$$

Module: `global_os.evals.environment.hrsn_experiment`.

## H-ORG family (split)

| Id | Claim |
|----|--------|
| H-ORG-1 | Specialization > identical general workers on heterogeneous tasks |
| H-ORG-2 | Recursive hierarchy > star after coordination scale threshold |
| H-ORG-3 | Independent verification plane reduces escaped errors enough to pay cost |
| H-ORG-4 | Adaptive compiler > best *static* policy on mixed **distribution** |

Task classes: highly_parallel · mixed_dependencies · strongly_sequential.  
Topologies: strong_single · manager_workers · recursive_hierarchy ·
hierarchy+independent_verification · adaptive.

Kill criteria for recursive default unchanged.  
`scientific_claim_accepted` stays false until live long-horizon evidence.

Module: `global_os.evals.organization.hypotheses`.

## H-EVAL-001 / H-CTX-001

Unchanged: calibrated evaluators (GOS-I24); structured context vs compaction.

## Capability self-audit

`audit_capability_matrix()` — claim vs implementation/tests/runtime/adversarial/
long-horizon/external evidence. Overstated production claims → `CLAIM OVERSTATED`.

## Experiment format

id, hypothesis, baseline, intervention, dataset/tasks, metrics, success_threshold,
kill_threshold, budget, preregistered_at, results, verdict, reopen_condition,
`scientific_claim_accepted`.

## Primary project score

$$
AutonomyEfficiency = \frac{VerifiedUsefulWork}{HumanAttention \times UnverifiedTrust \times Cost}
$$

Subject to Goal Integrity Score = PASS.
