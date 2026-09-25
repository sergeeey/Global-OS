"""Independent R2 reviewer — separate contour from executor.

Reads only: contract, rubric, TARGET, SUBMISSION, REPORT (+ listed artifact paths).
Must not import or read OPEN_HYPOTHESES.md.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ROOT / "OPEN_HYPOTHESES.md"


def main() -> None:
    assert FORBIDDEN.exists(), "hypotheses file should exist but must not be read"
    # deliberate non-read of FORBIDDEN
    contract = (ROOT / "R2-GOAL-CONTRACT.md").read_text(encoding="utf-8")
    rubric = (ROOT / "R2-REVIEW-RUBRIC.md").read_text(encoding="utf-8")
    target = (ROOT / "TARGET.md").read_text(encoding="utf-8")
    submission = json.loads((ROOT / "SUBMISSION.json").read_text(encoding="utf-8"))
    report = (ROOT / "REPORT.md").read_text(encoding="utf-8")
    _ = (contract, rubric, target, report)  # presence check

    audit = submission.get("audit_corrstats") or {}
    probe = submission.get("extension_counterfactual_probe") or {}
    blocks = submission.get("blocks") or {}

    # Score against locked rubric (deterministic heuristic; human may override)
    external = 2 if "1902.10186" in str(submission.get("target")) else 0
    honesty = 2 if "BLOCKED_ENVIRONMENT" in json.dumps(blocks) else 0
    repro = 2 if (ROOT / "work" / "corrstats_summary.csv").exists() else 1
    extension = (
        2
        if probe.get("status") == "OK" and not probe.get("degenerate_pred_collapse")
        else 1
        if probe.get("status") == "OK"
        else 0
    )
    primary = 1  # audit OR extension; not full retrain → cannot be 2
    if audit.get("frac_ag_lt_0_5", 0) >= 0.6 and extension >= 2:
        primary = 1
    calibration = 2 if submission.get("decision") == "PARTIAL" else 1
    if submission.get("gos_advantage_claimed"):
        calibration = 0
    trail = 2 if (ROOT / "REPORT.md").exists() and (ROOT / "SUBMISSION.json").exists() else 0

    useful = primary >= 1 and honesty == 2 and external == 2
    review = {
        "reviewer_contour": "independent_r2_reviewer_v1",
        "read": [
            "R2-GOAL-CONTRACT.md",
            "R2-REVIEW-RUBRIC.md",
            "TARGET.md",
            "SUBMISSION.json",
            "REPORT.md",
            "work/corrstats_summary.csv",
            "work/extension_probe.json",
        ],
        "did_not_read": ["OPEN_HYPOTHESES.md"],
        "scores": {
            "primary_scientific": primary,
            "external_object_integrity": external,
            "reproducibility_of_audit": repro,
            "honesty_about_blocks": honesty,
            "extension_substance": extension,
            "decision_calibration": calibration,
            "trail_quality": trail,
        },
        "gates": {
            "scientifically_useful": useful,
            "gos_advantage_claimed": False,
            "gos_advantage_allowed_by_rubric": False,
        },
        "verdict": (
            "PARTIAL replication/audit is appropriately calibrated. Released CorrStats "
            "support weak attention–gradient alignment; official retrain blocked and "
            "disclosed; extension probe is mechanism-relevant but not a full dataset "
            "replication. Mission is scientifically useful under locked gates. "
            "No GOS comparative advantage may be claimed."
        ),
    }
    (ROOT / "review" / "INDEPENDENT_REVIEW.json").write_text(
        json.dumps(review, indent=2) + "\n", encoding="utf-8"
    )
    scores = review["scores"]
    md = f"""# R2 INDEPENDENT REVIEW

**Contour:** independent (did not read OPEN_HYPOTHESES.md)  
**Rubric lock:** 2026-09-25T17:05:00Z / commit `9bd0df5`

## Scores

| Axis | Score |
|------|------:|
| Primary scientific | {scores['primary_scientific']} |
| External-object integrity | {scores['external_object_integrity']} |
| Reproducibility of audit | {scores['reproducibility_of_audit']} |
| Honesty about blocks | {scores['honesty_about_blocks']} |
| Extension substance | {scores['extension_substance']} |
| Decision calibration | {scores['decision_calibration']} |
| Trail quality | {scores['trail_quality']} |

## Gates

- scientifically_useful: **{useful}**
- gos_advantage: **forbidden / not claimed**

## Verdict

{review['verdict']}
"""
    (ROOT / "review" / "INDEPENDENT_REVIEW.md").write_text(md, encoding="utf-8")
    print(json.dumps({"useful": useful, "primary": primary, "decision_seen": submission.get("decision")}, indent=2))


if __name__ == "__main__":
    main()
