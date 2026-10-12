# Effect Receipt — mcp-bouncer Pilot 2 sealed fixes

**Status:** `RECONCILED` (external merge of F01–F07) + `CI_DEBT` (Ruff red on merge tip)  
**Pilot upstream:** `PILOT2-ENG-AB-v1`  
**Date (UTC):** 2026-10-12  
**GOS pack on main:** `#24` / `57c2938`

## Split claims (do not collapse)

| Claim | Status | Evidence |
|-------|--------|----------|
| F01–F07 merged to mcp-bouncer default branch | **RECONCILED** | PR [#6](https://github.com/sergeeey/mcp-bouncer/pull/6) merge `33030e35d9c7546cb263092da37b4f17ccb366e8` @ 2026-10-12T13:41:50Z |
| Local / post-merge regression tests | **VERIFIED_RUNTIME** | 62 passed (`PYTEST_POST_MERGE.txt`) |
| GitHub Actions on merge commit | **FAILED** | Ruff: RUF022, I001, PLE2515, PLE2502 |
| Full green CI after style fix | **PENDING** | Apply `mcp-bouncer-ci-ruff-fix.patch` → new PR; do not merge until green |

```text
Proposal ≠ Effect     — closed for F01–F07 (merge observed)
ToolCallSuccess       — pytest ≠ full CI green
CI debt               — separate short PR; not a rollback of the effect
PRODUCTION_PROVEN     — still NO
```

## Chain

```text
Observation (Pilot 2 sealed repro: 7 fail + 1 pass)
  → Correction proposal (F01–F07 pack)
  → Human authorization + push
  → External PR #6 merge ✅ 33030e3
  → Re-verify pytest ✅ 62
  → GitHub CI Ruff ❌ → CI-fix patch PROPOSED (bot 403 on push)
```

## External effect (F01–F07)

| Field | Value |
|-------|-------|
| Repo | https://github.com/sergeeey/mcp-bouncer |
| PR | https://github.com/sergeeey/mcp-bouncer/pull/6 |
| Merge commit | `33030e35d9c7546cb263092da37b4f17ccb366e8` |
| Base before | `45af09215daf106c74a21764290082a5c54583d4` |
| Actor | human `@sergeeey` (not autonomous bot merge) |

## CI-fix follow-up (style only)

| Field | Value |
|-------|-------|
| Local fix commit | `4492416112f72c02d98d29c24a1d625c4c766aee` (unpushed; bot 403) |
| Patch | `mcp-bouncer-ci-ruff-fix.patch` |
| Apply guide | `WINDOWS_APPLY_CI_RUFF.md` |
| Local ruff after fix | All checks passed (`RUFF_POST_FIX.txt`) |
| `guard.py` behavior change | none |

## Honesty

Do **not** claim full WorldSuccess until CI debt is cleared.  
Do **not** un-reconcile the F01–F07 merge because of Ruff.
