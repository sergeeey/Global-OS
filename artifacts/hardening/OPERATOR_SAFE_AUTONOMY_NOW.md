# OPERATOR — SAFE_AUTONOMY after MCID lock

M1.5 closed. Benchmark metrics frozen. Variance pilot done. **Do not re-run 48h.**

## Provenance (locked)

```text
EXAM_SHA     = 7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb
AUDIT_SHA    = a7960d9616c9c08224f5be9e1e7097bca9744bd0
BENCHMARK    = SAFE_AUTONOMY_BENCHMARK-v1 (METRICS_FROZEN, arms_started=false)
MCID         = SET_BY_VARIANCE_PILOT_v1
  mier_win_abs     = 0.04
  ssr_win_abs      = 0.18
  mier_approx_eps  = 0.02
PILOT_CLASS  = SYNTHETIC_DETERMINISTIC_FAULT_SANDBOX  (≠ T1 result)
```

## Now

1. **Next = real T1 arms A/B/C** under equal budgets (Mode A + Mode B report).
2. Arm C = thin Mission Assurance eval harness first — **no silent T0/T1 promote**.
3. Score with locked MCID; write `T1_DECISION.md` KEEP|REJECT only after score freeze.
4. Do **not** treat synthetic pilot gaps as evidence for H_TRUST.

## Sanity

```powershell
Set-Location C:\dev\Global-OS
git pull origin main
$env:PYTHONPATH = "$PWD\src"
python -m pytest -q tests/test_safe_autonomy_benchmark_v1.py tests/test_variance_pilot.py
```

Expect: green; freeze `mcid.status=SET_BY_VARIANCE_PILOT_v1`; `arms_started=false`.
