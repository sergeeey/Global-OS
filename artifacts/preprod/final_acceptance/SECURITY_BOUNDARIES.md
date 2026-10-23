# SECURITY_BOUNDARIES — PREPROD_SUPERVISED

| Boundary | Enforcement |
|----------|-------------|
| Authority before effect | `AuthorityKernel.decide` then `ToolGateway.execute` only |
| Sole produce | Handler inside Gateway; no pre-Authority produce |
| Capability ⊆ Goal ∩ Brief ∩ catalog | `resolve_allowed_tool_ids` + `assert_tool_permitted` |
| Args validation | `validate_tool_args` fail-closed |
| Path escape | `workspace_io._resolve_under` rejects `..` and abs paths |
| Write capability | `workspace.write_text` requires `filesystem.write` |
| Observation honesty | Gateway `OBSERVATION_PENDING`; post-exec verify only |
| Secrets | Via model adapters only; not in Goal JSON |
| Live LLM | Explicit operator authorize flag; Groq free tier |
| Challenge-GA | Not started |
| External irreversible writes | Not enabled beyond sandbox target writes |

Residual: HMAC action-binding hardening not claimed solved (`NOT_CLAIMED_SOLVED` in delivery limits).
