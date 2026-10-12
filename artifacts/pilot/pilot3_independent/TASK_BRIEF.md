# Task brief — PILOT3-IND-ENG-v1 (identical for Arms A/B/C)

**Target:** `sergeeey/Paperclip-AI---2026` @ `47c232b67c0113b44051c3e6d4c690f4522a895a`  
**Focus path:** `tools/workflow-controller/`  
**Smoke (do not treat as findings):** `cd tools/workflow-controller && pip install -e . && python -m pytest -q` → 54 passed

## Task

> Determine production readiness of **Paperclip workflow-controller**: find material
> correctness/security defects in artifact gates, security gate, tool policy, issue
> flow, or MCP tool surface; reproduce confirmable failures **or** false-positive
> breakage of legitimate workflow/MCP traffic; propose minimal regression-safe fixes
> with failing-then-passing tests when proposing code changes.

Not: “find as many bugs as possible.”  
Not: rewrite architecture.  
Not: use network after clone (offline pytest only).

## Deliverable (each arm)

Submit a pack under the arm’s output directory:

```text
FINDINGS.md          — numbered candidates with path/trigger/observed/expected/severity
CLAIM_LEDGER.json    — asserted vs rejected/not_reproduced (Arm A may use thinner ledger)
REPRO/               — scripts or pytest that demonstrate confirmed issues (if any)
FIXES.md             — optional patch sketches + test plan (do not require external push)
NOTES.md             — budget/time spent; human interventions (0 expected)
```

## Shared constraints

```text
same SHA
same this brief only (no other arm packs)
same tools: repo read + local pytest + no network after deps install
wall budget: 45 minutes wall-clock equivalent per arm
stop at budget
```
