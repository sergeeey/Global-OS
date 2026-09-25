# OPEN_HYPOTHESES — Y22 Arm B

## H_B1 — Last-claim-wins
Keep latest non-invalidated claim per (subject,predicate).

## H_B2 — Distrust high SRC ids after corruption signal
After any RETRACT/INVALIDATE, prefer SRC1–SRC6 over SRC7–SRC12 for slot resolution.

## H_B3 — Corroboration required
Active answer only if ≥2 distinct sources agree on value among non-invalidated claims.

## H_B4 — Earliest surviving low-SRC claim
Among active claims for a slot, prefer lowest SRC number then earliest t.
