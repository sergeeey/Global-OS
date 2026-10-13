# PREPROD + CTC integration tip

**Integration SHA:** `1372671`  
**Status:** MERGED_TO_MAIN — supervised read-only Operator + CTC v0  
**Challenge-GA:** `NOT_STARTED` (unchanged; not authorized)  
**Pre-production release:** NOT DECLARED

## Merge stack

| PR | Content | Tip before merge |
|----|---------|------------------|
| #43 | PREPROD_V0_1 Operator path (semantic criterion bind) | `1a77371` |
| #44 | Contextual Task Compiler v0 (empty-tools fail-closed) | `7fe7309` / merge `1372671` |

## What this tip claims

- `gos mission start|status|pause|resume|cancel|deliver` supervised read-only path
- Completion honesty: no false SUCCESS from bare receipts / bare `sc_01` id
- CTC: deterministic Execution Brief; no PromptKernel; briefs ≠ completion

## What it does not claim

- Live multi-hour LLM missions
- PRODUCTION_PROVEN / Continual SI
- Universal semantic verification of arbitrary goals
- Challenge-GA exec

## Operator

See [OPERATOR.md](OPERATOR.md). Clean-install pilot should independently inspect `delivery.json`.
