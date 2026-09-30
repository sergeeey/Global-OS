# Y24 Isolation Hard Gate — sealed holdout

**Status:** `ISOLATION_GATE_LOCKED`  
**Protocol:** `Y24-AVCT-v1`

## Hard gate (binding)

> No person or agent that **implements or tunes** arm C (adaptive verifier) or
> its **memory layer** may access sealed holdout labels/outcomes before unseal
> for execution scoring.

Also applies to:

```text
threshold fishing on holdout
prompt tuning against holdout labels
memory seed construction from holdout cases
```

## Role split

| Role | May see `public/` + DEV pack | May see `sealed/` holdout labels |
|------|------------------------------|----------------------------------|
| Corpus curator / stratum scorer | yes (DEV) | yes **only while sealing** (write-once), then stop |
| Arm A implementer | yes | **no** until execution unseal |
| Arm B implementer | yes | **no** until execution unseal |
| Arm C / memory implementer | yes | **no** until execution unseal |
| Blind scorer | n/a | yes after SHA freeze (read-only) |
| Decision writer | summary metrics only | via scorer outputs |

After holdout is `FROZEN_UNSEEN`, curator access ends. Re-opening sealed labels
for C development = **pack integrity fail** → INCONCLUSIVE or INVALID.

## Technical controls (eval harness)

1. Sealed files live under `artifacts/y24/sealed/` with manifest + sha256.
2. Arm runners receive only task payloads from `public/` / unsealed execution views
   that **strip** danger labels and stratum keys until score time.
3. Harness refuses arm execution if `holdout_status != UNSEALED_FOR_EXECUTION`.
4. Arm C memory store may ingest **DEV pack failures only** before unseal;
   holdout-derived memory seeds forbidden.
5. Leakage check: any sealed path read by arm process → fail closed + invalidate run.

## H_memory isolation

Repeat probes must be **unseen variants** of class X:

```text
first encounter:  case X1  (may be DEV or earlier execution fold)
second encounter: case X2  with same failure_class, different task_id/repo/patch
✗ X2 must not be byte-identical or trivial rename of X1
```

Literal memorization of the same case is **not** H_memory support.
