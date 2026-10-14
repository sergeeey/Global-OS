# RC CHANGES_REQUESTED — code fixes

Response to human verdict + GitHub review on PR #49 / #50.

| Pri | Finding | Fix |
|-----|---------|-----|
| P0 | `research.scan` empty sources/claims still verify ok | `verify_research_scan` requires non-empty sources **and** claims |
| P0 | `workspace.write_text` overwrite marked reversible | Default `allow_overwrite=False`; proposal `reversible=False` when target exists; produce fail-closed `overwrite_forbidden` |
| P0 | Exact-line only from criterion description | Falsifiers use full Goal Contract text (`objective` + criteria) |
| P0 | Exact-line substring match | Full-line equality (`line.strip() == marker`); punctuation stripped from capture |
| P1 | Sandbox signals never reach settle | Read `hooks.sandbox_signals` into substrate assessment |
| P1 | Nested JSON in markdown fences truncated | `extract_json_object` balanced-brace parse |

Regressions: `tests/test_rc_review_p0_regressions.py`.

**Still not claimed:** `PREPRODUCTION_ACCEPTED`, Challenge-GA, PRODUCTION_PROVEN. Human RELEASE_GATE remains 0/10 until second-machine acceptance.
