# Human handoff — mcp-bouncer sealed fixes

**Blocked:** `git push` to `sergeeey/mcp-bouncer` returns **403** for `cursor[bot]`  
(same class as PhaseBreak hygiene).

## Minimal operator steps

1. Apply `mcp-bouncer-pilot2-sealed-fixes.patch` on top of `45af092`.
2. Run `python -m pytest tests/ -q` → expect 62 passed.
3. Optionally re-run Global-OS sealed repro against the checkout → expect 8 passed.
4. Push branch + open PR (or paste patch into GitHub UI).
5. After merge, reply with PR URL + merge SHA so GOS can mark `EFFECT_RECEIPT` → `RECONCILED`.

## Non-claims until RECONCILED

- External acceptance
- Production readiness of mcp-bouncer
- Full F07 FP remediation (`sudo` in backticks still HIGH)
