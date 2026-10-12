# mcp-bouncer — Pilot 2 sealed-findings fix (WorldInteraction)

**Status:** `PROPOSED` — patch ready; external push blocked (`cursor[bot]` 403)  
**Base pin:** `sergeeey/mcp-bouncer@45af092`  
**Local fix commit:** `c0d493dfd6580d50d73d92d26a9056792904bbb9` (branch `gos/pilot2-sealed-fixes`)  
**Date (UTC):** 2026-10-12

## Why

Pilot 2 sealed repro (`artifacts/pilot/pilot2_eng_ab/repro/`) documented material defects.  
This pack turns audit findings into a **regression-safe external correction proposal**.

```text
Proposal ≠ Effect — effect not yet observed (awaiting human push/PR/merge)
```

## Local verification (this environment)

| Suite | Result |
|-------|--------|
| `tests/` (post-fix) | **62 passed** — see `PYTEST_OUT.txt` |
| Sealed Pilot 2 repro | **8 passed** (was 7 fail + 1 pass) — see `SEALED_REPRO_POST_FIX.txt` |

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

## Human apply (same path as PhaseBreak)

```powershell
cd D:\path\to\mcp-bouncer   # or clone fresh @ 45af092
git checkout -b gos/pilot2-sealed-fixes
git apply path\to\mcp-bouncer-pilot2-sealed-fixes.patch
# or: git am < patch
python -m pytest tests/ -q
git add -A
git commit -m "fix: close Pilot 2 sealed findings (F01-F07 core)"
git push -u origin gos/pilot2-sealed-fixes
# open PR → merge → reply with PR URL + merge SHA
```

Patch file: `mcp-bouncer-pilot2-sealed-fixes.patch`

## After external merge

Update `EFFECT_RECEIPT.md` → `RECONCILED` with PR URL + merge SHA + post-merge pytest on target main.  
Until then status stays `PROPOSED`.
