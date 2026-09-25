# REAL_USE_RULES.md — binding for R-missions after R1–R3

**Status:** Process constraint (not a new T0/T1 subsystem)

## Independent review

For R4+ real-use missions:

1. Lock Goal Contract + Review Rubric **before** terminal artifacts.
2. Executor must **not** write usefulness scores into the review contour.
3. Independent reviewer must not read `OPEN_HYPOTHESES.md`.
4. R1-style sole self-EVALUATION is insufficient for external-validity claims.

## Historical artifacts

- Do not rewrite `artifacts/y17|y19|hardening/dogfood_fm` in-place from tests.
- Use `GOS_MISSION_ARTIFACT_ROOT` isolation; `GOS_ALLOW_HISTORICAL_ARTIFACT_REWRITE=1` only when intentional.

## SHA binding

Y20–Y22 `public_pack_sha256` = directory merkle of `public/` (see `artifacts/r3/work/SHA_BINDING_NOTE.md`).

## Ops split

CRM/Docker/Reflexio/GeoScan: `artifacts/ops/SEPARATE_BACKLOG.md` — fresh observe first.
