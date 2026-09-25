# ENV incident — wrong cwd / wrong git repo (2026-09-25)

**Class:** `BLOCKED_ENVIRONMENT` (Gate A: env repair → same SHA may continue)  
**Not:** runtime/code defect · not invalidation of freeze `5d15600`

## Observation

Operator ran from `C:\Users\serge` (home / Claude vault git):

- branch: `fix/quality-v13`
- HEAD: `92e93bd7bdd5cbb02f130868111c7330376ce82f`
- `git checkout --detach 5d15600256a7afc7839f190ed3d889b33bc3217b`
  → `fatal: unable to read tree (5d15600…)`

That tree object does not exist in the home-dir repo. Smoke was not started.

## Classification

```text
environmental problem
→ repair environment (cd into Global-OS clone + identity gate)
→ document (this file)
→ same SHA 5d15600 may continue
```

## Repair (operator)

1. `cd` to clone (`C:\dev\Global-OS` or `%USERPROFILE%\Global-OS`).
2. Pass Step 0a identity gate in `M15_EXAM_KICKOFF.md`.
3. Detach `5d15600` → smoke.

Do **not** patch freeze SHA for this incident.
