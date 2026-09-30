# Y24 Isolation Attestation

**Status:** `BLANK — required before execution unseal`

When holdout is sealed and stubs are ready, each arm-C / memory implementer
(agent or human) must append:

```text
role: arm_C_or_memory_implementer
identity: <git author or agent id>
attestation: I did not access artifacts/y24/sealed holdout labels/outcomes
             while implementing or tuning arm C / memory.
date_utc: <ISO8601>
```

Empty attestation at unseal time → refuse execution.
