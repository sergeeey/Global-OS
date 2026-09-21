# Tasktracker

## Done

- [x] Sprint 0 docs + constitution + NON_GOALS + AGENTS
- [x] Core JSON schemas
- [x] ADR-0001 system boundaries
- [x] Repo/Python skeleton + CI
- [x] Goal Contract + Event Ledger
- [x] Authority Kernel stub + Tool Gateway guards
- [x] Epistemic invalidation minimal path
- [x] Null result memory
- [x] Model/Tool adapter interfaces
- [x] CLI (`gos goal create|show`, `gos events tail`)
- [x] Budget kernel
- [x] OrgUnit manager-workers + repo-audit DAG
- [x] Survival Benchmark scaffold
- [x] SQL persistence (SQLite now; Postgres-compatible schema)
- [x] DurableRunner crash/recovery (Temporal-shaped; ADR-0002)
- [x] Approval token signing (HMAC, one-time, action_hash-bound)
- [x] Cedar policies + PolicyEngine (default-deny)
- [x] Process-kill survival harness
- [x] Single-agent vs manager-workers baseline eval

## Next

- [ ] Postgres runtime (psycopg) behind same SQL schema
- [ ] Temporal adapter wiring
- [ ] Rust Authority service boundary
- [ ] Worker execution loop + artifact store
- [ ] Verification Router
- [ ] Repo-audit toolset (killer use case end-to-end)
