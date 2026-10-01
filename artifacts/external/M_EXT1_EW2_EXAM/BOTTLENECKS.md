# M-EXT1 Bottlenecks (split)

## A — Intrinsic to urllib3 task (not GOS defects)

- Needed editable install of urllib3 worktree (`_version` missing on bare PYTHONPATH).
- Issue repro is clear; root cause sits in a small, well-localized read loop.
- `blocksize=1` wire framing splits payload (detector nuance), not a product bug.

## B — Global OS / process observations from this exam

- Exam executed as agent+harness workflow; no live multi-day scheduler was required
  for this scoped incident (hours-scale, not multi-day).
- No Trust Kernel / memory / adaptive-verifier failure appeared as a blocker.
- Operator-facing status still manual (`STATUS.md` / ledger files) — packaging/UX gap,
  not a correctness failure on urllib3.
- Budget envelope (6h / 40 runs / 0 GOS edits) was sufficient; no envelope exhaust.

## C — Do **not** promote architecture from this

No recurring GOS failure pattern here that justifies ImmuneMemory / AdaptiveVerifier /
Trust Kernel changes. EW1 remains queued as the next external science exam.
