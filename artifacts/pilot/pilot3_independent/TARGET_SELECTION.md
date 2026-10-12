# Target selection — PILOT3-IND-ENG-v1

## Required properties

```text
real repository with imperfect tests
locally runnable offline after clone
plausible material defects
not Global-OS / PhaseBreak / Pilot-2-contaminated tip for this executor
safe sandbox (no live secrets required)
```

## Exclusion

| Repo | Why |
|------|-----|
| `sergeeey/Global-OS` | self-test contamination |
| `sergeeey/PhaseBreak-2026` | Pilot 1 target |
| `sergeeey/mcp-bouncer@45af092` / `@6ccce71` | Pilot 2 mined by this executor family — ENG contamination |
| `sergeeey/Claude-cod-top-2026` | prior wrong-repo exposure in same campaign |
| `sergeeey/ContextProof-2026` | 404 / unavailable |
| `sergeeey/Skeptic-Engine-2026-` | heavy data/scipy cost; metric-fishing risk |

## Shortlist (2026-10-12)

| # | Repo | Pin | Smoke | Decision |
|---|------|-----|-------|----------|
| 1 | `sergeeey/Paperclip-AI---2026` (`tools/workflow-controller`) | `47c232b` | 54 passed / 0.53s after `pip install -e .` | **SELECTED** |
| 2 | mcp-bouncer post-fix tip | `6ccce71` | green | REJECTED — contamination |
| 3 | Skeptic-Engine | tip | large | REJECTED — cost / fishing |
| 4 | Claude-cod-top | tip | 3600+ tests | REJECTED — exposure + weight |

## Freeze

```text
git clone https://github.com/sergeeey/Paperclip-AI---2026
git checkout 47c232b67c0113b44051c3e6d4c690f4522a895a
tree OID bde02dc5a9059a62e46db6b382606787d184250b
engineering focus: tools/workflow-controller
```
