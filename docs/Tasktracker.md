# Tasktracker

## Done

- [x] EnvironmentCompiler ecosystem + epistemic graph
- [x] Postgres + Temporal durable harnesses (live multi-worker)
- [x] OTel Workflow/Activity spans
- [x] Rust Authority process boundary + Python kernel wiring (`backend=rust`)

## Next

- [x] OTLP fail-closed config path (`configure_otlp_exporter` / `OtlpExportError`)
- [ ] Live OTLP collector export (production path; needs collector in CI/ops)
- [ ] Real-model eval runs replacing synthetic harnesses
- [ ] Default production profile to `GOS_AUTHORITY_BACKEND=rust` once ops-ready
- [ ] M2: deep repo-audit / strong sandbox / real multi-injection Survival
