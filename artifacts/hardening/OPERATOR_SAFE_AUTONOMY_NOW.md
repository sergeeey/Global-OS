# OPERATOR — post metrics freeze (SAFE_AUTONOMY_BENCHMARK-v1)

M1.5 is closed. Benchmark metrics are frozen. **Do not re-run 48h.**

## Provenance (locked)

```text
EXAM_SHA  = 7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb
AUDIT_SHA = a7960d9616c9c08224f5be9e1e7097bca9744bd0
BENCHMARK = SAFE_AUTONOMY_BENCHMARK-v1 (METRICS_FROZEN, arms_started=false)
```

## Now

1. Stay on current `main` (or a dogfood branch) — **do not patch** exam freeze SHA for H_TRUST.
2. Next scientific step = **variance pilot** (small N), then MCID amendment, then T1 arms A/B/C.
3. Arm C = thin Mission Assurance eval harness first — **no silent T0/T1 promote**.

## Sanity check (optional)

```powershell
Set-Location C:\dev\Global-OS
git pull origin main
$env:PYTHONPATH = "$PWD\src"
python -m pytest -q tests/test_safe_autonomy_benchmark_v1.py
```

Expect: all green; freeze JSON `status=METRICS_FROZEN`.
