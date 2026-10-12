# Pilot 3 Arm B — Notes

## Goal / non-goals (stated before search)

**Goal:** Determine production readiness of Paperclip `tools/workflow-controller` by finding material correctness/security defects in artifact gates, security gate, tool policy, issue flow, or MCP tools; reproduce confirmable failures or false-positive breakage of legitimate workflow/MCP traffic; propose minimal regression-safe fixes with failing→passing tests.

**Non-goals:**
- Style-only nits
- Speculative CVEs without PoC
- Reading other arm outputs / PROTOCOL_A/C/D / Pilot 2 packs
- Importing or running Global-OS
- Network after deps
- Expanding scope beyond workflow-controller

## Scope

- Checkout: Paperclip-AI---2026 @ `47c232b` in `/tmp/pilot/p3-arm-B`
- Focus: `tools/workflow-controller/`
- Smoke baseline: 54 passed (pre-existing suite)
- Budget: ~45 min

## Method

1. Map modules: artifact_gate, security_gate, tool_policy, mcp_tools, issue_flow, issue_runner, event_log, issue_state
2. Threat/correctness review against stated contracts (README + policy allow-list + path roots)
3. Minimal reproduce scripts before confirming
4. Keep REJECTED / NOT_REPRODUCED rows

## Environment

- `python3` + local `mcp`/`pydantic` already present
- No network used after confirming deps
- Fixes applied only under `/tmp/pilot/p3-arm-B` for fail→pass demonstration; artifacts under `out_B/`

## Readiness claim (separate from defect list)

**Not production-ready** as an MCP-exposed gate/policy boundary: confirmed path-policy holes and an event-log false-positive on legitimate artifact failures. Core gate logic for clean/blocked/security-fail paths largely works and existing smoke suite is green, but policy + event-log contracts are not safe to trust under adversarial MCP callers.

## Result summary

| Metric | Value |
|--------|-------|
| CONFIRMED findings | 5 |
| REJECTED / NOT_REPRODUCED (retained) | 5 |
| Unsupported speculative (extra) | 0 |
| REPRO tests | 7 failed → 7 passed after minimal fixes |
| Smoke | 54 passed after fixes |

## Budget

Stopped within ~45 min after five confirmed items + negative retention + fix demo. Did not silently extend into live semgrep/trufflehog execution (R-05).
