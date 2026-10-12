# Target selection — PILOT2-ENG-AB-v1

## Required properties

```text
medium-sized real repository
tests exist but imperfect
runtime locally runnable
several real bugs / claim inconsistencies plausible
not fully familiar to evaluator
safe sandbox execution
not Global-OS itself
not PhaseBreak (already used for Pilot 1 claims audit)
```

## Exclusion

| Repo | Why |
|------|-----|
| `sergeeey/Global-OS` | self-test contamination |
| `sergeeey/PhaseBreak-2026` | Pilot 1 target; different workload class already covered |
| Unrunnable / no tests | cannot verify findings |
| Secrets-heavy prod systems | unsafe |

## Candidate shortlist (evaluated 2026-10-12)

| # | Repo | Pin SHA | Why fit | Risk | Decision |
|---|------|---------|---------|------|----------|
| 1 | `sergeeey/mcp-bouncer` | `45af092` | stdlib-only; 50 tests / 0.04s; MCP injection filter; clear A/B failure modes | agent over-blocks MCP JSON-RPC | **SELECTED** |
| 2 | `sergeeey/ContextProof-2026` | — | API/RAG numeric invariants | heavier deps; stub-test risk | deferred (Pilot 2b) |
| 3 | `sergeeey/Skeptic-Engine-2026-` | — | adversarial metrics / leakage | high data cost; metric fishing | deferred (Pilot 3 class) |

## Selection rule

Prefer best **runnability × unfamiliarity × defect surface** under dual review.  
Document rejected candidates (no silent cherry-pick after peeking at results).

## Freeze

```text
git clone https://github.com/sergeeey/mcp-bouncer
git checkout 45af09215daf106c74a21764290082a5c54583d4
tree OID d85460b73de96aed6a8b71615577416b385e3bca
recorded in LOCK.json
```

Both arms receive an identical worktree at this pin. See `LOCK.json`.
