# mcp-bouncer — Pilot 2 sealed-findings fix (WorldInteraction)

**Status:** F01–F07 **RECONCILED** (PR #6 / `33030e3`); CI Ruff debt **PENDING**  
**Base pin (pre-fix):** `sergeeey/mcp-bouncer@45af092`  
**Merged tip:** `33030e35d9c7546cb263092da37b4f17ccb366e8`  
**Date (UTC):** 2026-10-12

## Why

Pilot 2 sealed repro → external correction. Merge landed; style CI still red.

```text
Proposal ≠ Effect — closed for F01–F07
Full CI green     — pending mcp-bouncer-ci-ruff-fix.patch (bot 403)
```

## Verification

| Suite | Result |
|-------|--------|
| `tests/` post-merge tip | **62 passed** — `PYTEST_POST_MERGE.txt` |
| Sealed Pilot 2 repro (pre-merge local) | **8 passed** — `SEALED_REPRO_POST_FIX.txt` |
| Ruff on merge tip | **FAIL** (4 errors) |
| Ruff after CI-fix patch (local) | **All checks passed** — `RUFF_POST_FIX.txt` |

## Fixes included

| Id | Change |
|----|--------|
| F01 | Optional whitespace after `;` `\|` `&&` in `command_injection` |
| F02 | Optional `your` in `ignore … previous` |
| F03 | `sanitize` maps invisibles → spaces (no keyword fusion) |
| F04 | NFKC + combining-mark fold before keyword scan |
| F05 | Optional `all` in `bypass … safety` |
| F06 | `$(…)` only with dangerous command (bare `$(date)` allowed) |
| F07 | `bash\|sh\|python` in backticks blocked (FP on routine `sudo` docs **not** fully resolved) |

## Human apply now (CI debt only)

F01–F07 already on mcp-bouncer `master` via [#6](https://github.com/sergeeey/mcp-bouncer/pull/6).  
Next: **`WINDOWS_APPLY_CI_RUFF.md`** + `mcp-bouncer-ci-ruff-fix.patch`.

## After CI-fix merges

Clear `CI_DEBT` in `EFFECT_RECEIPT.md` with CI-fix PR URL + merge SHA + green Actions.
