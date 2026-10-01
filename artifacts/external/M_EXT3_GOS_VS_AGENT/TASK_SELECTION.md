# M-EXT3 — Task selection gates (before pin)

**Status:** `SELECTION_OPEN`  
**Rule:** no `arms_started` until every gate below is `PASS` and
`TASK_PIN.json` exists.

## Must PASS

1. **External value** — answer useful outside Global OS (OSS bug / incident).
2. **Unknown a priori** — root cause not already solved in this repo’s artifacts.
3. **Not contaminated** — not urllib3#5248; not any issue already used in M-EXT1/EW2.
4. **Not EW1 retune** — not a science-label amendment of M-EXT2.
5. **Repro-capable** — pinned upstream SHA / commit exists; local repro plausible.
6. **Hard-gate compatible** — can apply M-EXT1-style gates:
   stable repro, competing explanations + counterevidence, patch eliminates,
   regression fail-before / pass-after (or honest REJECTED/INCONCLUSIVE).
7. **Non-degenerate expected** — not an already-closed upstream PR that only
   needs cherry-pick; not a docs-only issue; not “needs product decision only”.
8. **Budget-fit** — solvable or honestly inconclusive within the locked envelope
   (wall hours / scripted runs / hypothesis pivots).
9. **Dual-arm fair** — same public pack for A and B; no arm-private spoilers.
10. **License / ethics** — public issue; no credential hunting; no unauthorized access.

## Pin record (when ready)

Create `TASK_PIN.json` with at least:

```json
{
  "status": "TASK_PINNED",
  "issue_url": "...",
  "repo": "...",
  "working_sha": "...",
  "selection_gates_pass": true,
  "pinned_at_utc": "...",
  "contaminates_m_ext1": false
}
```

Until then: `STATUS.md` remains `PREREG_LOCKED_AWAITING_TASK_PIN`.
