# DECISION — PILOT2-ENG-AB-v1

**Status:** `TERMINAL`  
**Date (UTC):** 2026-10-12  
**Target:** `sergeeey/mcp-bouncer@45af092`  
**GOS tip at decision:** post-#22 (`9fa1fd6`)  
**Fidelity:** `SAME_EXECUTOR_DUAL_PROTOCOL` (see `arms/FIDELITY.md`)

## Terminal

```text
H-PILOT2-001 (higher verified useful work / cost·attention)
  = PARTIAL_SUPPORT_PROCESS_ONLY

Raw finding-count superiority of Global OS
  = NOT_SHOWN

Process / epistemic advantage (ledger, sealed repro, negative retention, FP catalog)
  = SUPPORTED under this fidelity

Intelligence advantage vs strong single agent
  = NOT_SHOWN
```

## Ordered evaluation

| # | Criterion | Result |
|---|-----------|--------|
| 1 | No critical invariant regression | PASS both |
| 2 | More confirmed useful findings | **Slight B** (9 vs 8; shared core) |
| 3 | Fewer unsupported/false | **Tie** (discipline better on B labeling) |
| 4 | Lower human attention | **A** (lighter) |
| 5 | Lower cost if quality equal | **INCONCLUSIVE** |

## What was verified on the target (independent of GOS win)

Material defects with sealed repro (`repro/test_confirmed_findings.py`, 7 fail + 1 pass):

- command_injection spacing bypasses
- `ignore your previous` miss
- sanitize→scan footgun (critical composition)
- `bypass all safety` miss
- `$(date)` / backtick FPs and `bash -c` bypass

Product claim `~90%` remains **unsupported** (no sealed corpus).

## Implications

1. Pilot 2 **does not** justify M2 “organization superiority.”
2. It **does** show a concrete product-shaped value: **engineering audits with honest terminals + repro packs**.
3. Next fidelity upgrade: separate executor/provider for A vs B, or human baseline.

## Non-claims

```text
≠ PRODUCTION_PROVEN
≠ Trust Kernel promote
≠ mcp-bouncer patches merged (audit-only; optional follow-up PRs)
≠ independent two-lab replication
```

## Artifacts

- `LOCK.json` (target + pins)
- `arms/ARM_A.md`
- `arms/ARM_B_CLAIM_LEDGER.json`
- `arms/FIDELITY.md`
- `repro/` + `repro/PYTEST_OUT.txt`
- `score/SCOREBOARD.json`
- `DECISION.md` (this file)
