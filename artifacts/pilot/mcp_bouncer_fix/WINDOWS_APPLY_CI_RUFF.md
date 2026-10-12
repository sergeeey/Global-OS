# Windows — restore green Ruff after mcp-bouncer PR #6

**Why:** PR #6 merged F01–F07 (`33030e3`); pytest 62 green; GitHub CI failed on Ruff only.  
**Bot:** still cannot push to `sergeeey/mcp-bouncer` (403). Human PR required.  
**Do not** amend #6; open a **new** PR from current `master`.

## Exact patch URL

| Kind | URL |
|------|-----|
| Raw (this CI-fix) | https://raw.githubusercontent.com/sergeeey/Global-OS/cursor/pilot3-abcd-handoff-2907/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-ci-ruff-fix.patch |
| After GOS PR #25 merges to main | https://raw.githubusercontent.com/sergeeey/Global-OS/main/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-ci-ruff-fix.patch |

(If #25 not yet merged, use the branch URL above or `git show` from a fetched Global-OS checkout.)

## PowerShell

```powershell
cd C:\dev\mcp-bouncer
git fetch origin
git status --short
git switch -c fix/pilot2-ci-ruff origin/master

$patch = "$env:TEMP\mcp-bouncer-ci-ruff-fix.patch"
# Prefer branch URL until Global-OS #25 is on main:
curl.exe -L --fail -o $patch `
  "https://raw.githubusercontent.com/sergeeey/Global-OS/cursor/pilot3-abcd-handoff-2907/artifacts/pilot/mcp_bouncer_fix/mcp-bouncer-ci-ruff-fix.patch"

Get-Content -TotalCount 8 $patch   # expect "From " / "diff --git"
git apply --check $patch
git apply $patch

python -m ruff check .
python -m pytest -q
git diff --check
git diff --stat
# expect: All checks passed! + 62 passed; only __init__.py + test_guard.py

git add mcp_bouncer/__init__.py tests/test_guard.py
git commit -m "ci: fix Ruff errors after Pilot 2 merge"
git push -u origin fix/pilot2-ci-ruff
```

PR title: `ci: restore green Ruff checks after Pilot 2 fixes`  
**Do not merge until GitHub CI is green.**

## What the patch changes

- Sort `__all__` (RUF022)
- Sort imports (I001)
- Escape `\u200b`, `\u00ad`, `\u2060`, `\u202e` in sanitize tests (PLE2515/PLE2502)
- **No** `guard.py` edits
