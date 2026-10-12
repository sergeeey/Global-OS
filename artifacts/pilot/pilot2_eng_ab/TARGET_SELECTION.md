# Target selection — PILOT2-ENG-AB-v1

## Required properties

```text
medium-sized real repository
tests exist but imperfect
runtime locally runnable
several real bugs / claim inconsistencies plausible
not fully familiar to evaluator
safe sandbox execution
not Global-OS itself
not PhaseBreak (already used for Pilot 1 claims audit)
```

## Exclusion

| Repo | Why |
|------|-----|
| `sergeeey/Global-OS` | self-test contamination |
| `sergeeey/PhaseBreak-2026` | Pilot 1 target; different workload class already covered |
| Unrunnable / no tests | cannot verify findings |
| Secrets-heavy prod systems | unsafe |

## Candidate shortlist (fill at lock)

| # | Repo | Pin SHA | Why fit | Risk |
|---|------|---------|---------|------|
| 1 | _TBD_ | | | |
| 2 | _TBD_ | | | |
| 3 | _TBD_ | | | |

## Selection rule

Prefer the candidate with the best **runnability × unfamiliarity × defect surface** score under dual review.  
Document rejected candidates with one-line reason (no silent cherry-pick after peeking at results).

## Freeze

Once chosen:

```text
git clone --filter=blob:none <url>
git checkout <pin_sha>
record tree OID + pin in LOCK.json
```

Both arms receive an identical tarball / worktree snapshot.
