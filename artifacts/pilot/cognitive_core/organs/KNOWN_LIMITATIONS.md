# Known limitations (honesty)

## DurableRunner (#31)

**Verified:** after `SUCCEEDED`, resume does not re-invoke the last step handler;
prior result fields remain (`test_succeeded_rerun_does_not_reexecute_last_step`).

**Not claimed:**
- full exactly-once for all external world effects
- crash **between** step side-effect and checkpoint write (no WAL dual-write protocol here)
- Temporal distributed exactly-once

If a step performs a non-idempotent external effect and dies before `COMPLETED`
checkpoint, re-run may double-effect unless the tool/idempotency_key layer prevents it.
That remains Tool Gateway idempotency + EffectReceipt territory — not solved by #31 alone.

## Organ stubs

Contracts locked; stubs refuse Challenge execution and do not claim Intelligence advantage.
