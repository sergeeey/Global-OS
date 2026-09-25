# R1 Goal Contract — Real-use mission

**mission_id:** `R1-EVIDENCE-INTEGRITY-v1`  
**track:** real-use (not synthetic A/B; not Y23)  
**model_pin:** composer-cloud-agent-bundle  
**architecture constraint:** ADR-0009 — no new T0/T1 surfaces; honesty/evidence only

## Objective (operator-valuable)

After Y20–Y22 showed **no measurable primary GOS advantage** on short controlled
probes, run one real mission:

> Make Global OS’s **claim ↔ evidence** surface auditable enough for continued
> real-use: find actionable integrity gaps in `docs/capability_matrix.json`
> (and adjacent freeze-binding metadata), falsify false alarms, apply **minimal**
> honesty remediations, and leave a regression so the gap class cannot silently
> return.

Not a goal: invent a metric where GOS “wins”; expand architecture; reopen Y20–Y22 scorers.

## Research question under test (practical)

> If GOS does not make the model smarter on short sealed probes, can the same
> disciplined loop produce **useful, reproducible, low-intervention** work on a
> real integrity problem the operator would keep?

## Invariants

- Do not retune Y20–Y22 scorers / weights / MCID / generators
- Do not start Y23 / LH / M1.5 / Continual SI claims
- Do not mutate frozen Y20–Y22 arm freeze artifacts
- Do not add T0/T1 architectural surfaces
- Prefer: evidence-path honesty, regression tests, downgrades — over new subsystems
- Operator interventions: minimize; record every one

## Method (GOS loop)

```text
observe → competing hypotheses → experiments → falsify → revise → terminal
```

## Stop rules (terminal)

Stop when **all** hold:

1. Primary hypotheses for this mission are SUPPORTED / REJECTED / INCONCLUSIVE with evidence
2. Accepted remediations (if any) are applied + regression exists
3. Independent eval rubric (locked before remediations) is filled
4. `decision.md` + `CLAIMS.md` written; no universal-advantage claim

## Deliverables

| Artifact | Role |
|----------|------|
| `R1-EVAL-RUBRIC.md` | Locked **before** remediations |
| `OPEN_HYPOTHESES.md` / `HYPOTHESIS_TRACE.json` | Competing claims |
| `findings/*.json` | Confirmed / rejected findings |
| matrix + test patch | Minimal remediations |
| `EVALUATION.md` | Independent post-hoc scoring of usefulness |
| `decision.md` / `CLAIMS.md` | Terminal |

## Explicit non-goals

Y23 · sealed science rescue · LH preflight · M1.5 · Continual SI · universal GOS advantage
