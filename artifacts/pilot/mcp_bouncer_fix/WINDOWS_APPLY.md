# Windows apply — mcp-bouncer F01–F07 (exact paths)

**Global-OS main SHA (pack landed):** `57c29388077f7a96a8ba850c8affd15cd4f1ebb7` (#24)  
**Target repo:** https://github.com/sergeeey/mcp-bouncer  
**Target pin:** `45af09215daf106c74a21764290082a5c54583d4`  
**Patch path in Global-OS:** `artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch`

## Exact URLs (do not search the whole disk)

| Kind | URL |
|------|-----|
| Browse | https://github.com/sergeeey/Global-OS/blob/main/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch |
| Raw (download) | https://raw.githubusercontent.com/sergeeey/Global-OS/main/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch |
| Pack README | https://github.com/sergeeey/Global-OS/blob/main/artifacts/pilot/mcp_bouncer_fix/README.md |

Bot **cannot** push to `sergeeey/mcp-bouncer` (403). Human GitHub access required.

## PowerShell — download patch without corrupting encoding

```powershell
# Prefer curl.exe (binary-safe). Avoid Out-File / `>` (UTF-16 risk on PS 5.1).
$patch = "$env:TEMP\mcp-bouncer-pilot2-sealed-fixes.patch"
curl.exe -L --fail -o $patch `
  "https://raw.githubusercontent.com/sergeeey/Global-OS/main/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch"

# Sanity: must start with "From " or "diff --git"
Get-Content -TotalCount 5 $patch
Select-String -Path $patch -Pattern '^diff --git' | Select-Object -First 3
```

## PowerShell — apply on clean mcp-bouncer @ 45af092

```powershell
cd C:\dev\mcp-bouncer   # your clone path
git status --short
git fetch origin
git checkout 45af09215daf106c74a21764290082a5c54583d4
git switch -c fix/gos-verified-findings

$patch = "$env:TEMP\mcp-bouncer-pilot2-sealed-fixes.patch"
git apply --check $patch
git apply $patch
git diff --check
git diff --stat

python -m pytest tests/ -q
# expect: 62 passed

# Optional sealed repro from Global-OS (after fetch):
# python -m pytest C:\dev\Global-OS\artifacts\pilot\pilot2_eng_ab\repro\test_confirmed_findings.py -q
# expect: 8 passed

git add mcp_bouncer/guard.py tests/test_guard.py
git commit -m "fix: close GOS Pilot 2 sealed findings (F01-F07 core)"
git push -u origin fix/gos-verified-findings
# open PR → merge → reply with PR URL + merge SHA
```

## Alternate: extract from local Global-OS after fetch

```powershell
cd C:\dev\Global-OS
git fetch origin
git rev-parse --short origin/main   # expect 57c2938 or later containing the pack
git show "origin/main:artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-pilot2-sealed-fixes.patch" |
  Set-Content -Encoding utf8NoBOM "$env:TEMP\mcp-bouncer-pilot2-sealed-fixes.patch"
# If utf8NoBOM unavailable (PS 5.1), use curl.exe method above instead.
```

## PR body notes (security / API)

- Behavior change: `sanitize()` now maps invisibles → **spaces** (was delete) to prevent keyword fusion.
- Detection tightened: spacing bypasses, `ignore your previous`, `bypass all safety`, NFKC fold, `bash|sh|python` backticks.
- FP reduced: bare `$(date)` no longer HIGH.
- Not claimed fixed: routine `` `sudo ...` `` docs may still HIGH (F07 residual).

## RECONCILED gate

Do **not** mark effect reconciled on push alone. Need:

```text
merge SHA on target default branch
+ post-merge pytest (62) and/or sealed repro (8)
→ then Global-OS EFFECT_RECEIPT.md → RECONCILED
```
