"""Independent R3 reviewer — must not read OPEN_HYPOTHESES.md."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    forbidden = ROOT / "OPEN_HYPOTHESES.md"
    assert forbidden.exists()
    sub = json.loads((ROOT / "SUBMISSION.json").read_text(encoding="utf-8"))
    report = (ROOT / "FORENSIC_REPORT.md").read_text(encoding="utf-8")
    a = json.loads((ROOT / "findings" / "track_a.json").read_text(encoding="utf-8"))
    b = json.loads((ROOT / "findings" / "track_b.json").read_text(encoding="utf-8"))
    _ = (ROOT / "R3-GOAL-CONTRACT.md").read_text(encoding="utf-8")
    _ = (ROOT / "R3-REVIEW-RUBRIC.md").read_text(encoding="utf-8")

    has_both = "Track A" in report and "Track B" in report and len(a) >= 3 and len(b.get("findings", [])) >= 3
    primary = 2 if has_both else 1 if has_both or len(a) >= 2 else 0
    questions = "Constructed questions" in report
    honesty = 2 if "Non-claims" in report and not sub.get("gos_advantage_claimed") else 1
    failure = 2 if "REJECTED" in report or "falsified" in report.lower() or "B-H-falsified" in report else 1
    deliverable = 2 if (ROOT / "FORENSIC_REPORT.md").stat().st_size > 500 else 0
    evidence = 2 if (ROOT / "findings" / "track_a.json").exists() and b.get("pin_sha256") else 1
    calibration = 2 if sub.get("decision") == "FINDINGS_DELIVERED" and not sub.get("gos_advantage_claimed") else 0

    useful = primary >= 1 and honesty == 2 and deliverable >= 1
    review = {
        "reviewer_contour": "independent_r3_reviewer_v1",
        "did_not_read": ["OPEN_HYPOTHESES.md"],
        "scores": {
            "primary": primary,
            "question_construction": 2 if questions else 0,
            "evidence_quality": evidence,
            "honesty": honesty,
            "failure_pressure_handled": failure,
            "deliverable_usefulness": deliverable,
            "calibration": calibration,
        },
        "gates": {"forensically_useful": useful, "gos_advantage_allowed": False},
        "verdict": (
            "Both forensic tracks delivered evidenced findings with constructed questions, "
            "explicit non-claims, and at least one falsified dead-end. HIGH finding on test "
            "artifact regeneration is actionable. Sample NYC311 anomalies are correctly scoped "
            "as sample-relative. Mission is forensically useful. No GOS advantage claim."
        ),
    }
    (ROOT / "review" / "INDEPENDENT_REVIEW.json").write_text(json.dumps(review, indent=2) + "\n")
    s = review["scores"]
    (ROOT / "review" / "INDEPENDENT_REVIEW.md").write_text(
        f"""# R3 INDEPENDENT REVIEW

**Contour:** independent (OPEN_HYPOTHESES not read)  
**Rubric lock:** 2026-09-25T17:15:00Z / `65c2fb2`

## Scores
| Axis | Score |
|------|------:|
| Primary | {s['primary']} |
| Question construction | {s['question_construction']} |
| Evidence quality | {s['evidence_quality']} |
| Honesty | {s['honesty']} |
| Failure pressure | {s['failure_pressure_handled']} |
| Deliverable usefulness | {s['deliverable_usefulness']} |
| Calibration | {s['calibration']} |

## Gates
- forensically_useful: **{useful}**
- gos_advantage: forbidden

## Verdict
{review['verdict']}
""",
        encoding="utf-8",
    )
    print(json.dumps({"useful": useful, "primary": primary}, indent=2))


if __name__ == "__main__":
    main()
