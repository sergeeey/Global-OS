# LH-COGNITIVE wall_48h — operator raw PASS (pre-audit)

**Status:** harness PASS recorded; **M1.5 NOT CLAIMED** until independent audit  
**Exam SHA:** `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`  
**Protocol:** LH-COGNITIVE-v1

## Locked gates observed (operator report)

```text
fidelity        = COGNITIVE_WALL_CLOCK_48H
passed          = true
wall_seconds    = 172801.2008432  (>= 172800)
m15_claimed     = false
git_sha         = 7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb
workload_class  = EXTERNAL_RESEARCH_OBJECT
```

Start local: 2026-09-28 00:21:43  
Finish local: 2026-09-30 00:21:52  

## Raw artifact roots (do not edit)

- `artifacts/hardening/long_horizon_48h/windows_cognitive_wall_48h/`
  - `program_report.json`
  - `PASS_CRITERIA.json`
  - `EXAM_START.json`
  - `missions/` (evidence + review pack)
- Prior smoke: `os_kill_smoke_windows_cognitive/`
- Prior preflight: `windows_cognitive_preflight/`
- Reboot interrupt backup (not a PASS): `_bak_reboot_interrupt_20260928_000436/`

## Next

1. Freeze/copy raw tree (hash or zip) without mutation  
2. Independent audit contour (executor must not self-certify M1.5)  
3. Scope-limited M1.5 decision only after audit  

Claim template: `docs/SCIENTIFIC_HONESTY_MAP.md` + `M15_CLAIM_FORK.md` (Variant B cognitive).
