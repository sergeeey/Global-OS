# PREREG — PILOT2-ENG-AB-v1

**Status:** `DRAFT` — lock SHA before arm start  
**Protocol id:** `PILOT2-ENG-AB-v1`  
**Primary hypothesis:** `H-PILOT2-001` (see `GOAL_CONTRACT.md`)

## Lock sequence

```text
1. Choose target repo + pin commit (TARGET_SELECTION.md)
2. Seal rubrics (this file + FINDING_RUBRIC.md + METRICS.md)
3. Record provider/model/tool/budget pins
4. Run A and B (order randomized or A-then-B with no cross-leak)
5. Score with sealed rubric
6. Publish DECISION.md
```

Amendments after lock require a written `PREREG_AMENDMENT.md` **before** unseal of scores.

## Provider / budget pins (fill before lock)

| Pin | Value | Notes |
|-----|-------|-------|
| Model family | _TBD_ | same for A and B |
| Provider | _TBD_ | same |
| Tool set | _TBD_ | same allowlist |
| Wall budget | _TBD_ | e.g. 4h each |
| Token/API budget | _TBD_ | comparable |
| Network policy | _TBD_ | same |
| Human help policy | scripted interventions only; counted |

## Ordered evaluation (primary)

Do **not** collapse to a single magic number.

```text
1. No critical invariant regression (Authority / safety / data loss).
2. More confirmed useful findings (B vs A).
3. Fewer unsupported / false findings (B vs A).
4. Lower human attention for comparable quality.
5. Lower cost where quality is equivalent.
```

Gate (1) fails → arm FAIL regardless of findings count.

## Secondary outcomes (pre-registered)

| Id | Statement | Win if |
|----|-----------|--------|
| S1 | Provenance completeness higher under B | checklist Δ ≥ sealed threshold |
| S2 | Negative results retained under B | no silent drop of REJECTED paths |
| S3 | Restart/resume preserves B state | cold resume smoke PASS |
| S4 | Goal drift lower under B | sealed drift score |

Thresholds filled at lock (variance pilot optional; default: qualitative PASS/FAIL with dual coder).

## Terminal vocabulary

| Verdict | Meaning |
|---------|---------|
| `SUPPORTED` | H-PILOT2-001 holds under ordered eval |
| `REJECTED` | A dominates on primary ordered criteria |
| `TIE_WITHIN_TOLERANCE` | Comparable quality; no clear advantage |
| `INCONCLUSIVE` | Protocol break, budget incomparability, or target unsound |

## Forbidden after lock

```text
change primary metric
weaken baseline tools
give B extra docs/secrets
retune OrgCompiler mid-run for score
discard negative findings
```

## Relationship to PhaseBreak

Pilot 1 proved claim-audit value; advantage **NOT_MEASURED**.  
Pilot 2 measures advantage on **engineering** workload.  
PhaseBreak hygiene is a separate WorldInteraction cycle, not an arm of Pilot 2.
