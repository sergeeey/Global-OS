# Tasktracker

## Done

- [x] EnvironmentCompiler ecosystem + epistemic graph
- [x] Postgres + Temporal durable harnesses (live multi-worker)
- [x] OTel Workflow/Activity spans
- [x] Rust Authority process boundary + Python kernel wiring (`backend=rust`)
- [x] OTLP fail-closed config path (`configure_otlp_exporter` / `OtlpExportError`)
- [x] IndependentVerificationStack (GOS-I10 multi-method diversity)
- [x] Deep repo audit (deterministic static depth)
- [x] Multi-injection Survival harness (4 additional RUNTIME_INJECTED)
- [x] Strong sandbox fail-closed port (ADR-0006; live Docker optional)

## Next

- [ ] Live OTLP collector export (production path; needs collector in CI/ops)
- [ ] Real-model eval runs replacing synthetic harnesses
- [ ] Default production profile to `GOS_AUTHORITY_BACKEND=rust` once ops-ready
- [ ] CI Docker harness for live container isolation (promote sandbox_strong to HARNESS)
- [ ] Remaining Survival injections (API_OUTAGE, MODEL_SWAP, …)
- [ ] Remote multi-provider verification adapters (beyond local multi-method)
- [ ] H-ORG-001 measured baselines
