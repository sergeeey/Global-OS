# Upstream-ready deliverable pack — urllib3#5248

| Artifact | Path |
|----------|------|
| Issue pin | `../EW2_oss_incident/EW2_PIN.json` |
| Issue snapshot | `../EW2_oss_incident/ISSUE_SNAPSHOT.json` |
| Repro matrix | `../EW2_oss_incident/repro/repro_matrix.py` |
| Repro logs | `../EW2_oss_incident/repro/logs/` |
| Competing explanations | `../EW2_oss_incident/COMPETING_EXPLANATIONS.md` |
| Root cause | `../EW2_oss_incident/ROOT_CAUSE.md` |
| Proposed patch | `../EW2_oss_incident/proposed_fix.diff` |
| Regression test | `../EW2_oss_incident/repro/test_regression_blocksize_zero.py` |
| Before/after pytest logs | `repro/logs/regression_BEFORE_patch.txt`, `regression_AFTER_patch.txt` |

Suggested upstream PR body: link #5248, explain `read(0)` semantics, include regression test.
