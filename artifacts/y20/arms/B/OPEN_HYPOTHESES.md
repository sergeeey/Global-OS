# OPEN_HYPOTHESES — Arm B

## H_B1 — Correlation-dense graph
Unconditional high-|r| pairs oriented by index/coef asymmetry recover enough
structure for intervention regression.

## H_B2 — Conditional independence sparsens usefully
Partial-correlation screening removes spurious edges; remaining sparse DAG parents
improve interventional forecasts (internal fold MAE).

## H_B3 — Path-aware adjustment required
Simple parent adjustment of target is insufficient; need explicit mediator path
blocking / front-door style proxies for `do()` forecasts.

## H_B4 — Effect is mostly size/noise (null)
No method beats predicting target mean; structure claims unsupported.
