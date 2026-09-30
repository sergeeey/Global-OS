# SAFE_AUTONOMY PACK-v2 — FREEZE (unseen / sealed)

**Status:** `UNSEALED` (was `FROZEN_UNSEEN` until T2)  
**Freeze time (UTC):** 2026-09-30T10:10:00Z  
**Unsealed for:** `SAFE_AUTONOMY_T2-v1` @ experiment SHA `e6dfd08c0c83e15a25bebc6c8a11a38e48bc0bd3`  
**Purpose:** holdout pack for T2 redesign — **not** for rescoring T1.

## Rules (binding)

1. T1 remains **REJECT** under pack v1 + locked MCID forever for that experiment.
2. PACK-v2 must stay **sealed** until a preregistered T2 protocol explicitly unseals it.
3. Mission Assurance redesigns must **not** be tuned against pack v1 cases after reading this freeze.
4. If T2 needs MCID, it comes from a **new independent pilot** on pack v2 (or a declared pilot split) — never from T1 residuals applied to T1.

## Sealed contents

Machine manifest: `PACK_V2_MANIFEST.json`  
Sealed blob: `sealed/sealed_pack.json` (hash-locked; do not open for arm training)

Public metadata only (this file + manifest): scenario class inventory, N, seed identity — **not** per-mission step payloads.

## Relationship to T1

| Item | Value |
|------|-------|
| T1 pack | `artifacts/safe_autonomy_t1/mission_pack/` (v1, public, already used) |
| T1 verdict | REJECT |
| PACK-v2 | reserved for future T2 only |
