# USER-DEFINED AUDIT RUBRIC — V1 CONTRACT

Status: **FROZEN CONTRACT**, no runtime implementation.

## Semantic problem

Two independent real projects exposed the same failure:

```text
fixed Global-OS-specific checklist
  -> false positives (CONSTITUTION.md / GOS-I01..I08)
  -> false negatives (CI, tests, dependencies, domain evidence)
  -> technical SUCCEEDED mistaken for readiness PASS
```

The contract below replaces project-specific semantic assumptions with
user-supplied criteria. It does not add a planner, memory, learning, recovery
redesign or arbitrary tool execution.

## Artifacts

| Artifact | Schema |
|---|---|
| AuditRubric | `audit_rubric.schema.json` root |
| Criterion | `audit_rubric.schema.json#/$defs/Criterion` |
| CriterionResult | `audit_result.schema.json#/$defs/CriterionResult` |
| AuditResult | `audit_result.schema.json` root |

Evidence is only what the runtime actually observes. A criterion result must
carry references or declare missing evidence; no fabricated evidence.

## Two independent verdict layers

```text
execution_terminal = SUCCEEDED | FAILED | INCONCLUSIVE
audit_verdict      = PASS | FAIL | UNKNOWN | MIXED
```

They are intentionally independent:

```text
runtime completed correctly + rubric FAIL     -> SUCCEEDED / FAIL
runtime completed correctly + rubric UNKNOWN  -> SUCCEEDED / UNKNOWN
runtime failed             + rubric may be N/A -> FAILED / ...
```

`SUCCEEDED` means the audit execution finished and produced a valid result. It
does **not** mean the user's goal, project readiness or domain claim passed.

## Criterion semantics

- `PASS`: actual evidence supports the statement, and `evidence_refs` is nonempty.
- `FAIL`: actual evidence contradicts the statement, or the criterion explicitly
  chooses missing evidence as FAIL, or evidence sources conflict.
- `UNKNOWN`: evidence is missing, inaccessible or insufficient; no fabricated
  PASS or FAIL.

Defaults:

```text
on_missing_evidence = UNKNOWN
on_conflict          = FAIL
pass_requires_evidence = true
```

Authors may explicitly set `on_missing_evidence = FAIL`; absence is never
converted to FAIL silently.

`required` controls aggregation only. It does not make missing evidence pass or
fail; it determines whether the result affects the overall audit verdict.

## Aggregation policy v1

Only one mode:

```text
mode = required_all_pass
```

Algorithm:

```text
1. If any required criterion is FAIL -> FAIL
2. Else if any required criterion is UNKNOWN -> UNKNOWN
3. Else all required are PASS:
     optional FAIL/UNKNOWN present and optional_issues = MIXED -> MIXED
     optional issues ignored or absent                         -> PASS
```

`optional_issues = IGNORE` means optional results are reported but do not affect
the verdict. `unresolved` lists UNKNOWN criteria and optional non-PASS criteria.

## Evidence binding

Allowed evidence reference kinds:

```text
file | directory | command | url | artifact | absence | other
```

References must point to actual observed files/outputs/artifacts. The contract
does not allow a runtime to invent evidence from a criterion statement. A
criterion's expected evidence is a request, not proof.

## Adversarial checks

| # | Check | Required behavior |
|---|---|---|
| 1 | No available evidence | `UNKNOWN`, not PASS/FAIL (unless criterion explicitly selects missing=FAIL) |
| 2 | Irrelevant criterion | Excluded by rubric author; runtime must not add Global-OS criteria |
| 3 | Conflicting evidence | never PASS; default FAIL (`on_conflict=FAIL`) |
| 4 | Optional criterion | does not block required result; MIXED or IGNORE per policy |
| 5 | Technical success | `execution_terminal=SUCCEEDED` may coexist with audit `FAIL`/`UNKNOWN` |
| 6 | Project type | no project-type field and no project-specific branching required |
| 7 | Malformed/ambiguous criterion | rejected before audit execution by schema/validation |

Malformed examples rejected by contract: missing `id`, invalid ID pattern,
empty `statement`, missing `expected_evidence`, no required criterion, duplicate
`id`, unknown aggregation mode, invalid verdict/terminal string.

The JSON Schema enforces field shape; the pre-execution semantic validator must
also enforce criterion-ID uniqueness and reject duplicate IDs. The result
validator must reject a `criterion_id` not present in the rubric and must reject
missing required criterion results.

Concrete checks:

```text
examples/adversarial/missing_evidence.result.json  -> UNKNOWN
examples/adversarial/conflict.result.json          -> FAIL, never PASS
examples/adversarial/optional_mixed.result.json    -> MIXED
examples/adversarial/invalid_empty.rubric.json     -> schema rejection
```

## Y17 fit

Rubric: `examples/y17.rubric.json`; result: `examples/y17.result.json`.

Criteria are derived from the project's actual research-handoff question:
clean-clone tests, dependency completeness, CI, reproducibility, data contracts,
external/local-only dependencies, research evidence, handoff docs.

Result demonstrates the critical separation:

```text
execution_terminal = SUCCEEDED
audit_verdict      = FAIL
```

Root cause is actual evidence: fresh-clone test collection failure, no CI, no
lock, dependency mismatch; not missing Global-OS constitution.

## mcp-bouncer fit

Rubric: `examples/mcp_bouncer.rubric.json`; result:
`examples/mcp_bouncer.result.json`.

Criteria: package/test reproducibility, CI, zero-dependency claim, security
benchmark, FP/FN evidence, threat model/red-team, operational limitations,
handoff docs.

Result:

```text
execution_terminal = SUCCEEDED
audit_verdict      = UNKNOWN
```

Tests, CI and zero dependencies PASS; security benchmark, FP/FN and red-team
evidence are UNKNOWN, not fabricated FAIL/PASS. This is the intended behavior.

## No project-specific hardcoding

The schema has no `project_type`, no `constitution`, no `gos_invariants`, no
`requires_schema` or any Y17/mcp-bouncer field. Criteria are user data. The same
schema produced both examples with different criteria and different outcomes.

## Implementation scope for the next milestone

`USER-DEFINED-AUDIT-RUBRIC-V1-IMPLEMENTATION-1` should be limited to:

1. load a rubric and reject malformed/ambiguous criteria before execution;
2. use a bounded read-only evidence collector for declared file/directory/
   absence evidence (and reuse accepted read-only inventory where available);
3. replay/derive CriterionResult with PASS/FAIL/UNKNOWN and evidence refs;
4. apply only the frozen aggregation algorithm;
5. return AuditResult with execution terminal and audit verdict separated;
6. no automatic Global-OS criteria, no LLM planner, no memory/learning, no
   arbitrary tool use, no target writes.

If a criterion needs evidence the bounded collector cannot obtain, the result is
`UNKNOWN` — never invented.

## Freeze

```text
contract: audit-rubric/1
result:   audit-result/1
frozen_at: 2026-11-06
```

Schemas/examples are frozen with this document. No runtime code is part of this
milestone.
