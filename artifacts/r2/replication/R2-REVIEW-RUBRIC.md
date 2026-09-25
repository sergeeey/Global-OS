# R2 Independent Review Rubric

**Locked at:** `2026-09-25T17:05:00Z`  
**Lock rule:** frozen before executor terminal decision.  
**Reviewer contour:** separate from executor; may read only:
- `R2-GOAL-CONTRACT.md`
- this rubric
- `TARGET.md`
- `SUBMISSION.json`
- `REPORT.md`
- cited artifact paths listed in SUBMISSION

Must **not** read `OPEN_HYPOTHESES.md`, executor scratch notes, or rewrite experiments.

## Primary scientific score (0–2)

| Score | Meaning |
|------:|---------|
| 0 | Main claim not assessed or contradicted by audit without explanation |
| 1 | Partial: released evidence audited OR extension only; full retrain absent |
| 2 | Strong: released evidence + independent probe both align with claim under stated scope |

## Axes (0–2)

| Axis | 0 | 1 | 2 |
|------|---|---|---|
| External-object integrity | Internal toy / our generator | Mixed | Clear external paper+code |
| Reproducibility of audit | Cannot replay | Partial scripts | Scripted aggregation + probe |
| Honesty about blocks | Hidden skips | Mentioned | Explicit BLOCKED + impact |
| Extension substance | None / cosmetic | Minor | Mechanism-relevant probe |
| Decision calibration | Overclaim | OK | Matches evidence strength |
| Trail quality | Opaque | Partial | Hypotheses→falsify→terminal |

## Gates

- Call mission **scientifically useful** iff Primary ≥ 1 **and** Honesty=2 **and** External=2  
- Call **GOS advantage** — **FORBIDDEN** from this rubric (not measured)

## Output

Write `review/INDEPENDENT_REVIEW.md` + `review/INDEPENDENT_REVIEW.json` with scores and 5–10 line verdict.
