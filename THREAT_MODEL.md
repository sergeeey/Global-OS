# THREAT_MODEL.md

**Status:** Baseline — must exist before first external tool.

## Actors

malicious webpage · malicious repo · malicious MCP server · compromised model/provider · malicious/buggy worker · compromised dependency · malicious user · stale evidence · fake tool success · memory poisoning · goal hijacking

## Primary failure modes

| Mode | Mitigation direction |
|------|----------------------|
| goal drift | Immutable versions + amendment protocol |
| authority escalation | Child ⊆ parent; kernel outside model |
| memory poisoning | Typed epistemic store + taint |
| evidence laundering | Status machine + provenance |
| fake verification | Diversity requirements (GOS-I10) |
| agent collusion | Independent verification plane |
| cascading summary error | Artifact-first |
| infinite loop / budget explosion | Budget kernel + stop engine |
| duplicate external effect | idempotency_key pipeline |
| tool result spoofing | Effect receipt reconciliation |
| stale source | Invalidation engine |
| partial action | reserve → execute → record → reconcile |
| organizational bureaucracy | H-ORG-001 kill criteria |
| manager bottleneck | Span-of-control + metrics |

## Trust zones

T0 immutable without human; Authority Kernel never trusts model output as policy input.

## Untrusted Reader

External → restricted reader → typed extraction → schema validation (in code) → trusted reasoning plane.
