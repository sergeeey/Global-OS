# mcp-bouncer — Pilot 2 sealed-findings fix (WorldInteraction)

**Status:** F01–F07 **RECONCILED** + CI repair **CI_VERIFIED**  
**Base pin (pre-fix):** `sergeeey/mcp-bouncer@45af092`  
**Final master tip:** `6ccce718ba8c0361806269e9d7a29e4f0842c6fc` (#7)  
**Date (UTC):** 2026-10-12

## Why

Pilot 2 sealed repro → external correction → CI debt closed.

```text
Proposal ≠ Effect — closed (#6)
CI debt after #6  — closed (#7 + green master push)
```

## Verification

| Suite | Result |
|-------|--------|
| `tests/` | **62 passed** |
| Sealed Pilot 2 repro (pre-merge local) | **8 passed** — `SEALED_REPRO_POST_FIX.txt` |
| PR #7 checks | 3.11/3.12/3.13 PASS |
| master push after #7 | **success** run `38261957403` |

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

## Closed

See `EFFECT_RECEIPT.md`. Historical apply notes remain in `WINDOWS_APPLY.md` / `WINDOWS_APPLY_CI_RUFF.md`.
