# H_TRUST revival triggers

**Status:** `FIRED_T2_KEEP`  
**JSON:** `REVIVAL_TRIGGERS.json`

```text
T1 REJECT under pack v1          = immutable
T2 KEEP on PACK-v2               = selective recovery continues MA line
RT-1 + RT-2                      = fired via T2
Trust Kernel / T0–T1 promote     = still FORBIDDEN (ADR-0012)
```

T2 is not a rescue that rewrites T1. It is a new preregistered experiment on the sealed holdout pack.
