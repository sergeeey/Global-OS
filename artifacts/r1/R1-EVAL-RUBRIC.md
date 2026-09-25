# R1 Independent Evaluation Rubric

**Locked at:** `2026-09-25T16:17:08Z`  
**Lock rule:** this file’s criteria MUST NOT change after remediations begin.  
**Scorer:** human/operator or separate agent; **not** the same run self-certifying “useful” without checklist.

## Axes (0–2 each; integers only)

| Axis | 0 | 1 | 2 |
|------|---|---|---|
| **Usefulness** | Operator would discard | Partial keep (notes only) | Operator keeps artifact / fix in trunk |
| **Reproducibility** | Cannot re-run | Re-run needs tribal knowledge | Scripted/regression; third party can replay |
| **Evidence trail** | Missing/opaque | Partial hypotheses/logs | Full observe→hyp→falsify→decision trail |
| **Autonomy** | Heavy operator steering | Occasional nudges | ≤1 recorded intervention for mission scope |
| **Cost discipline** | Unbounded / thrash | Noticeable waste but finished | Scoped; no architecture tourism |
| **Honesty** | Overclaim / hide nulls | Mixed | Nulls preserved; no universal advantage claim |

**Primary usefulness gate:** Usefulness ≥ 1 **and** Honesty = 2 required to call R1 “worth repeating as R2 template”.  
**Autonomy gate (secondary):** Autonomy ≥ 1. Secondary cannot override honesty failure.

## Explicit forbidden rescues

- Changing rubric after seeing outcomes
- Claiming GOS primary sealed/reliability advantage from R1
- Counting synthetic Y20–Y22 retunes as R1 success

## Fill-in (post terminal only)

See `EVALUATION.md` — must cite this lock timestamp.
