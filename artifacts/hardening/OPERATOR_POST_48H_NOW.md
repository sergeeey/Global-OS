# OPERATOR — post 48h: freeze → independent audit (NOW)

Stay on exam tree with artifacts. Scripts can be pulled from `origin/main` without switching HEAD.

## One block (PowerShell)

```powershell
Set-Location C:\dev\Global-OS
$h = (git rev-parse HEAD).Trim()
if ($h -ne "7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb") { throw "STOP: exam HEAD changed" }

# 1) ensure sources exist
@(
  "artifacts\hardening\long_horizon_48h\windows_cognitive_wall_48h\program_report.json",
  "artifacts\hardening\long_horizon_48h\windows_cognitive_preflight\program_report.json",
  "artifacts\hardening\long_horizon_48h\os_kill_smoke_windows_cognitive"
) | ForEach-Object { if (-not (Test-Path $_)) { throw "missing $_" } }

# 2) fetch audit script from main (do NOT checkout main onto exam SHA)
git fetch origin main
New-Item -ItemType Directory -Force -Path "$env:TEMP\gos_audit" | Out-Null
git show origin/main:artifacts/hardening/audit_cognitive_48h/freeze_and_audit.py |
  Set-Content -Encoding utf8 "$env:TEMP\gos_audit\freeze_and_audit.py"

# 3) freeze + independent audit (writes freeze pack + INDEPENDENT_REVIEW)
$env:PYTHONPATH = "$PWD\src"
python "$env:TEMP\gos_audit\freeze_and_audit.py" --repo-root "$PWD" `
  --freeze-root "$PWD\artifacts\hardening\freeze_lh_cognitive_7ab345e" `
  --out "$PWD\artifacts\hardening\audit_cognitive_48h\out"

# 4) show recommendation
Get-Content artifacts\hardening\audit_cognitive_48h\out\INDEPENDENT_REVIEW.md
```

**Expect:** `m15_recommendation = M1.5_CANDIDATE_SCOPE_LIMITED`, `all_gates_passed = true`.  
If freeze_root already exists from a partial run → move it to `_bak_*` first.

## Then paste back

```powershell
Get-Content artifacts\hardening\audit_cognitive_48h\out\INDEPENDENT_REVIEW.json
```

Cloud will lock `M15_DECISION.md` from that JSON.
