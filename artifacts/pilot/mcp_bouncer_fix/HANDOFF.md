# Human handoff — mcp-bouncer

## Status

| Item | State |
|------|-------|
| F01–F07 external merge | **DONE** — PR #6 → `33030e3` → EffectReceipt **RECONCILED** |
| Pytest | **62 passed** |
| GitHub CI on merge tip | **FAILED** (Ruff) |
| CI-fix PR | **YOUR ACTION** — bot 403; patch ready |

## Your P0 now

1. Apply `mcp-bouncer-ci-ruff-fix.patch` from current `master` (see `WINDOWS_APPLY_CI_RUFF.md`).
2. Open PR `ci: restore green Ruff checks after Pilot 2 fixes`.
3. Wait for **green** GitHub CI, then merge.
4. Reply with CI-fix PR URL + merge SHA → we clear `CI_DEBT` / mark CI `VERIFIED`.

## Exact raw URL (CI-fix; branch until GOS #25 merges)

```
https://raw.githubusercontent.com/sergeeey/Global-OS/cursor/pilot3-abcd-handoff-2907/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-ci-ruff-fix.patch
```

## Non-claims

- Full green CI until the new PR merges
- PRODUCTION_PROVEN
- Rollback of F01–F07 (not warranted)
