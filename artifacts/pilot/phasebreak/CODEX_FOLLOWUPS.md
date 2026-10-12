# Codex P2 follow-ups after PhaseBreak PR #1

**Source:** automated review on https://github.com/sergeeey/PhaseBreak-2026/pull/1  
**Hygiene merge:** `0161463` — still valid; these are **next** doc consistency fixes.

| Id | Finding | Suggested action |
|----|---------|------------------|
| PB-F1 | Nikkei: analysis vs JSON may be pre-fix vs post-fix, not unresolved forever | Reframe `NIKKEI_FAILURE_ANALYSIS.md` as historical pre-fix; cite JSON as post-fix |
| PB-F2 | Paper still says commodities recall 50% while README/JSON say 67% | Align `paper/main.tex` prose or explicitly demote paper for that number |
| PB-F3 | Paper still has stronger “universality” wording vs README “not confirmed” | Align paper or stop claiming CORRECTIONS↔paper alignment complete |
| PB-F4 | `crypto` labeled `benchmark-validated` with null P/R and no JSON domain | Downgrade crypto status until metrics exist |

**Rule:** do not metric-fish the pipeline to “fix” these; docs/authority-of-sources only.
