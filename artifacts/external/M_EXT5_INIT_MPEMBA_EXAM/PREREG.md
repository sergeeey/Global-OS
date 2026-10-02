# M-EXT5 Preregistration — LOCKED

**Protocol:** `M-EXT5-INIT-MPEMBA-v1`  
**Locked after:** mechanical gate GREEN + pilot reconnaissance  
**Machine:** `PREREG.json`

## Pilot amendment record

Pilot (seeds 10–14) showed:

- LATE target 0.35: 0/5 hot wins  
- EARLY target 1.0: 5/5 hot wins  

Therefore primary H_EFFECT locks to **LATE** (aligned with “final regime”).  
EARLY locked as **secondary** endpoint only.

## Primary decision (H_EFFECT)

| Item | Value |
|------|-------|
| Valid pair | D_hot0 > D_cold0 |
| Endpoint | τ to train batch CE ≤ 0.35 |
| Success | τ_hot < τ_cold |
| n | 20 sealed pairs |
| Rule | SUPPORTED if n_wins ≥ 15 and Binom p<0.05; REJECTED if n_wins ≤ 12; else INCONCLUSIVE; INCONCLUSIVE if n_valid < 16 |

## Secondary (H_EFFECT_EARLY)

Same rule at loss ≤ 1.0. Cannot alone make mission H_EFFECT = SUPPORTED.

## H_FISHER

Only if H_EFFECT (late) SUPPORTED; else REJECTED (or INCONCLUSIVE if effect INCONCLUSIVE).  
Proxy: early grad-norm hot > cold; same 15/20 rule.

## Seal

`SEALED_HOLDOUT.json` — 20 pairs, seed_pair ∈ [1000,1019], batches from RNG entropy `0xE501BEEF`.  
SHA256 recorded in `PREREG.json` after seal write.

## Forbidden post-unseal

Endpoint change, threshold fishing, seed cherry-picking, M-EXT4 14/20 rule.  
