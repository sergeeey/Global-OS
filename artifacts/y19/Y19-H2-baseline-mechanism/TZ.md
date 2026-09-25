# Y19-H2 — Baseline mechanism (follow-up to H1 REJECTED)

**Prior:** Y19-H1 → `REJECTED` (`H_baseline_sufficient`).  
**New question (unknown a priori):** Is that baseline signal carried by early
**activity dynamics alone**, or do `{n, k, state_entropy}` improve sealed-holdout Brier by MCID?

## Competing hypotheses

1. **H_size_entropy_add_signal** — full baseline beats activity-only by MCID (≤0.90 Brier ratio).
2. **H_activity_core_sufficient** — size/entropy extras fail MCID (REJECTED primary).
3. **H_underpowered** — holdout balance insufficient.

## Seeds (new, sealed)

- Train: 2000–2179  
- Hold: 6000–6119  
- Disjoint from Y19-H1 and Y17 ranges.

## Decision

Same MCID family as H1; same NK simulator; **does not reopen H1**.
