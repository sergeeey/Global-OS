**Status:** `DONE` — PhaseBreak PR #1 merged `0161463` (see `artifacts/pilot/phasebreak/EFFECT_RECEIPT.md`)

# PhaseBreak hygiene — human handoff

**Status:** ~~waiting on human~~ → completed  
**Source pack:** `artifacts/pilot/phasebreak/PROPOSED_HYGIENE.patch`  
**After:** Global-OS #20 merged (`c851246`)

## Why this still matters

```text
Observation → Finding → Evidence → Decision → Correction
→ Repository state changes → Reverification
```

Until hygiene merges on PhaseBreak, external world effect is still only a proposal.

## Recommended commands (`D:\PhaseBreak-2026`)

```powershell
cd D:\PhaseBreak-2026
git status
git fetch origin
git switch main
git pull --ff-only
git rev-parse HEAD   # ideally fd1e55c tip used by pilot; else re-check patch
git switch -c gos/phasebreak-evidence-hygiene

# path to patch from Global-OS main:
#   artifacts/pilot/phasebreak/PROPOSED_HYGIENE.patch
git apply --check <PATH>\PROPOSED_HYGIENE.patch
git apply <PATH>\PROPOSED_HYGIENE.patch
git diff
```

Run PhaseBreak’s own claim-related checks / tests. Then:

```powershell
git add .
git commit -m "docs: reconcile claims with Global OS pilot evidence"
git push -u origin gos/phasebreak-evidence-hygiene
```

### Suggested PR title

`docs: reconcile benchmark claims with pilot evidence`

### Suggested body

```text
Source: Global OS PILOT-PB-CLAIMS-v1
Changes:
- commodities recall: 50% → 67%
- production-usable → benchmark-validated
- universality claim downgraded / not confirmed
- Nikkei provenance conflict explicitly marked unresolved
No algorithm/runtime behavior changed.
This PR only aligns public claims with existing benchmark artifacts.
```

## After PhaseBreak merge

Record effect in Global-OS:

```text
artifacts/pilot/phasebreak/EFFECT_RECEIPT.md
  - PhaseBreak PR URL
  - merge SHA
  - re-verify README numbers vs JSON
```
