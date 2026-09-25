# ENV incident — smoke on non-freeze SHA (2026-09-25)

**Class:** `BLOCKED_ENVIRONMENT` / operator sequencing  
**Not:** code defect on freeze · not Step 1 PASS for Gate A

## Observation

1. Correct clone: `C:\dev\Global-OS`, remote `sergeeey/Global-OS`.
2. `git checkout --detach 5d15600…` aborted: untracked  
   `artifacts/hardening/long_horizon_48h/os_kill_smoke_windows/os_kill_result.json`
   would be overwritten.
3. HEAD remained `bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee` (not freeze).
4. Operator still ran `os_process_kill` smoke → JSON `passed: true`.

## Classification

```text
Smoke PASS on non-freeze SHA = Windows env capability evidence ONLY
→ does NOT satisfy Gate A Step 1 (must be on exactly 5d15600)
→ move/backup conflicting untracked path
→ detach 5d15600
→ re-run smoke
→ only then Step 1 may PASS
```

Same freeze SHA remains valid (env / sequencing repair, not patch-and-continue).

## Note on M15_EXAM_KICKOFF.md = False before detach

That path exists on `main` / after detach to `5d15600` lineage that includes kickoff
docs. Absence on old HEAD `bfa58a0` is expected — not a missing clone.
