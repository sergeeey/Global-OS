# M-EXT2 — Goal Contract (EW1 science exam)

**Status:** `GOAL_LOCKED`  
**Exam id:** `M-EXT2-EW1`  
**Protocol:** `EW1-CTP-v1`  
**After:** M-EXT1 IMMUTABLE (`ROOT_CAUSE_CONFIRMED`)

## Goal (external scientific value)

Test whether early-window complexity features beat a strong simple baseline at
predicting long/chaotic transient labels on a coupled logistic-map lattice,
on a **sealed holdout**, under locked MCID.

Honest `SUPPORTED` / `REJECTED` / `INCONCLUSIVE` are all successful exam outcomes.

## Not

- Not Y19 reopen (different domain; Y19 FROZEN)
- Not GOS self-proof; not architecture shopping from M-EXT1
- Y24/Y25 not evidence

## Budget envelope (hard stop)

| Resource | Cap | On exhaust |
|----------|-----|------------|
| Wall investigation | **8 hours** | honest `INCONCLUSIVE` if no powered decision |
| Data regen / reseal after unseal | **0** | forbidden (Y24 lesson) |
| Post-hoc feature adds after unseal | **0** | forbidden |
| GOS code edits for score optics | **0** | forbidden |

## Decision hard gates

From prereg:

- Holdout Brier_candidate ≤ 0.90 × Brier_baseline **and**
- Same MCID after ablating `N` from candidate
- Else if class balance <12 pos/neg → `INCONCLUSIVE`
- Else → `REJECTED`

## EW2 / M-EXT1

Immutable — do not polish urllib3 further for GOS self-score.
