# R1 OPEN_HYPOTHESES

**Mission:** R1-EVIDENCE-INTEGRITY-v1  
**Status:** OPEN at observe

## H1 — Broken evidence paths

> Some `capability_matrix` evidence strings point to missing files.

**Falsify if:** every parseable `tests|artifacts|src|docs/...` path exists.

## H2 — Unparseable evidence (audit gap)

> A non-trivial set of capabilities have evidence prose with **no** parseable path, so maturity is not mechanically auditable.

**Falsify if:** <5 such entries OR all such entries are intentionally CONTRACTED docs-only.

## H3 — Freeze SHA unbound

> Y21/Y22 `process_log.public_pack_sha256` does not bind to the public pack used by arms (integrity defect).

**Falsify if:** recorded SHA equals harness `_dir_sha256(public_dir)` (directory merkle including README), i.e. apparent file-hash mismatch is a measurement error.

## H4 — Ambiguous entries are untested overclaims

> Capabilities with unparseable evidence lack automated tests and should be downgraded.

**Falsify if:** each such capability has ≥1 existing acceptance/harness test that exercises it.

## H5 — Minimal path-binding remediation is sufficient

> Adding parseable evidence paths + a matrix lint regression closes the audit gap **without** T0/T1 changes or maturity downgrades.

**Supported only if:** post-fix lint is green and no state downgrade required for H2 cohort.
