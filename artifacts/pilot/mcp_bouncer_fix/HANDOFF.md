# Human handoff — mcp-bouncer sealed fixes

**Blocked:** `git push` / fork / PR-from-bot to `sergeeey/mcp-bouncer` returns **403** for `cursor[bot]`  
(same class as PhaseBreak hygiene). Local fix commit exists; external effect still `PROPOSED`.

## Exact patch location (after Global-OS #24 merge)

| Field | Value |
|-------|-------|
| Global-OS main | `57c29388077f7a96a8ba850c8affd15cd4f1ebb7` |
| Path | `artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch` |
| Raw URL | https://raw.githubusercontent.com/sergeeey/Global-OS/main/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch |
| Target | https://github.com/sergeeey/mcp-bouncer @ `45af092` |

Full PowerShell steps: **`WINDOWS_APPLY.md`** (encoding-safe download via `curl.exe`).

## Minimal operator steps

1. Download patch from Raw URL above (do not search disk for F01 / random `.diff`).
2. Apply on `45af092`; run `pytest tests/ -q` → **62 passed**.
3. Optional: sealed repro → **8 passed**.
4. Push branch + open PR; note sanitize space-substitution + detection changes in PR body.
5. After **merge**, reply with PR URL + merge SHA → then `EFFECT_RECEIPT` → `RECONCILED`.

## Non-claims until RECONCILED

- External acceptance
- Production readiness of mcp-bouncer
- Full F07 FP remediation (`sudo` in backticks still HIGH)
- Effect from push alone (merge + re-verify required)
