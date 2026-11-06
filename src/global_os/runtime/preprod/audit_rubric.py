"""Minimal user-defined audit rubric runtime for audit-rubric/1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

_CONTRACT_DIR = Path(__file__).resolve().parents[4] / "docs" / "audit_rubric"


class AuditRubricError(Exception):
    """Invalid rubric or unsupported audit contract."""


def _schema(name: str) -> dict[str, Any]:
    path = _CONTRACT_DIR / name
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AuditRubricError(f"rubric contract schema unavailable: {path}") from exc
    if not isinstance(raw, dict):
        raise AuditRubricError(f"rubric contract schema is not an object: {path}")
    return raw


def _validate_semantics(rubric: dict[str, Any]) -> None:
    criteria = rubric.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise AuditRubricError("rubric must contain at least one criterion")
    seen: set[str] = set()
    required_count = 0
    for criterion in criteria:
        cid = str(criterion["id"])
        if cid in seen:
            raise AuditRubricError(f"duplicate criterion id: {cid}")
        seen.add(cid)
        if criterion.get("required") is True:
            required_count += 1
    if required_count == 0:
        raise AuditRubricError("rubric must contain at least one required criterion")


def load_rubric(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditRubricError(f"cannot read rubric: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AuditRubricError(f"malformed rubric JSON: {path}") from exc
    if not isinstance(raw, dict):
        raise AuditRubricError("rubric must be a JSON object")
    validator = Draft202012Validator(_schema("audit_rubric.schema.json"))
    errors = sorted(validator.iter_errors(raw), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(x) for x in first.path)
        raise AuditRubricError(f"rubric schema error at {location or '<root>'}: {first.message}")
    _validate_semantics(raw)
    return raw


def _relative_locator(target: Path, locator: str) -> Path | None:
    rel = Path(locator)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        return None
    path = (target / rel).resolve()
    try:
        path.relative_to(target.resolve())
    except ValueError:
        return None
    return path


def _missing_verdict(criterion: dict[str, Any]) -> str:
    rule = criterion.get("acceptance_rule") or {}
    return str(rule.get("on_missing_evidence") or "UNKNOWN")


def _evidence_ref(kind: str, path: Path, target: Path) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "kind": kind,
        "ref": path.relative_to(target).as_posix(),
    }
    if path.is_file():
        ref["hash"] = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
    return ref


def _unreadable(cid: str, locator: str, reason: str) -> dict[str, Any]:
    return {
        "criterion_id": cid,
        "verdict": "UNKNOWN",
        "reason": reason,
        "evidence_refs": [],
        "missing_evidence": [f"unreadable: {locator}"],
    }


def evaluate_criterion(target: Path, criterion: dict[str, Any]) -> dict[str, Any]:
    expected = criterion["expected_evidence"]
    kind = str(expected.get("kind") or "other")
    locator = expected.get("locator")
    cid = str(criterion["id"])
    rule = criterion.get("acceptance_rule") or {}
    rule_name = str(rule.get("rule") or "evidence_supports")
    if rule_name in {"custom", "evidence_conflicts"}:
        return {
            "criterion_id": cid,
            "verdict": "UNKNOWN",
            "reason": f"V1 cannot evaluate acceptance rule: {rule_name}",
            "evidence_refs": [],
            "missing_evidence": [f"unsupported acceptance rule: {rule_name}"],
        }
    if not isinstance(locator, str) or not locator:
        return {
            "criterion_id": cid,
            "verdict": "UNKNOWN",
            "reason": "criterion has no machine-readable locator",
            "evidence_refs": [],
            "missing_evidence": ["locator"],
        }

    path = _relative_locator(target, locator)
    if path is None:
        return {
            "criterion_id": cid,
            "verdict": "UNKNOWN",
            "reason": "locator is outside target or not a relative path",
            "evidence_refs": [],
            "missing_evidence": [locator],
        }

    if kind == "file":
        if path.exists() and not path.is_file():
            verdict = "FAIL" if str(rule.get("on_conflict") or "FAIL") == "FAIL" else "UNKNOWN"
            return {
                "criterion_id": cid,
                "verdict": verdict,
                "reason": "evidence conflict: expected file, observed directory",
                "evidence_refs": [_evidence_ref("directory", path, target)],
                "missing_evidence": [locator] if verdict == "UNKNOWN" else [],
            }
        if path.is_file():
            try:
                ref = _evidence_ref("file", path, target)
            except OSError:
                return _unreadable(cid, locator, f"expected file is unreadable: {locator}")
            return {
                "criterion_id": cid,
                "verdict": "PASS",
                "reason": "expected file exists (V1 checks presence only)",
                "evidence_refs": [ref],
                "missing_evidence": [],
            }
        verdict = "FAIL" if _missing_verdict(criterion) == "FAIL" else "UNKNOWN"
        return {
            "criterion_id": cid,
            "verdict": verdict,
            "reason": f"expected file is missing: {locator}",
            "evidence_refs": [],
            "missing_evidence": [locator],
        }

    if kind == "directory":
        if path.exists() and not path.is_dir():
            verdict = "FAIL" if str(rule.get("on_conflict") or "FAIL") == "FAIL" else "UNKNOWN"
            try:
                ref = _evidence_ref("file", path, target)
            except OSError:
                return _unreadable(cid, locator, f"conflicting file is unreadable: {locator}")
            return {
                "criterion_id": cid,
                "verdict": verdict,
                "reason": "evidence conflict: expected directory, observed file",
                "evidence_refs": [ref],
                "missing_evidence": [locator] if verdict == "UNKNOWN" else [],
            }
        if path.is_dir():
            return {
                "criterion_id": cid,
                "verdict": "PASS",
                "reason": "expected directory exists (V1 checks presence only)",
                "evidence_refs": [_evidence_ref("directory", path, target)],
                "missing_evidence": [],
            }
        verdict = "FAIL" if _missing_verdict(criterion) == "FAIL" else "UNKNOWN"
        return {
            "criterion_id": cid,
            "verdict": verdict,
            "reason": f"expected directory is missing: {locator}",
            "evidence_refs": [],
            "missing_evidence": [locator],
        }

    if kind == "absence":
        return {
            "criterion_id": cid,
            "verdict": "UNKNOWN",
            "reason": "V1 cannot safely interpret absence evidence without a concrete absence predicate",
            "evidence_refs": [],
            "missing_evidence": [locator],
        }

    return {
        "criterion_id": cid,
        "verdict": "UNKNOWN",
        "reason": f"V1 does not support evidence kind: {kind}",
        "evidence_refs": [],
        "missing_evidence": [f"unsupported evidence kind: {kind}"],
    }


def aggregate(rubric: dict[str, Any], results: list[dict[str, Any]]) -> tuple[str, list[str]]:
    criteria = {str(c["id"]): c for c in rubric["criteria"]}
    verdicts = {str(r["criterion_id"]): str(r["verdict"]) for r in results}
    required = [cid for cid, c in criteria.items() if c.get("required") is True]
    optional = [cid for cid in criteria if cid not in required]
    unresolved = sorted(
        cid
        for cid in criteria
        if verdicts.get(cid) == "UNKNOWN"
        or (cid in optional and verdicts.get(cid) != "PASS")
    )
    if not required:
        return "UNKNOWN", sorted(criteria)
    if any(verdicts.get(cid) == "FAIL" for cid in required):
        return "FAIL", unresolved
    if any(verdicts.get(cid) != "PASS" for cid in required):
        return "UNKNOWN", unresolved
    if unresolved and rubric["aggregation_policy"]["optional_issues"] == "MIXED":
        return "MIXED", unresolved
    return "PASS", unresolved


def validate_result(
    result: dict[str, Any], rubric: dict[str, Any] | None = None
) -> dict[str, Any]:
    validator = Draft202012Validator(_schema("audit_result.schema.json"))
    errors = sorted(validator.iter_errors(result), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(x) for x in first.path)
        raise AuditRubricError(
            f"audit result schema error at {location or '<root>'}: {first.message}"
        )
    if rubric is not None:
        expected = [str(c["id"]) for c in rubric["criteria"]]
        actual = [str(r["criterion_id"]) for r in result["criterion_results"]]
        if len(actual) != len(expected) or set(actual) != set(expected):
            raise AuditRubricError(
                "audit result criterion set does not match rubric criteria"
            )
    return result


def evaluate_rubric(
    target: Path, rubric: dict[str, Any], execution_terminal: str
) -> dict[str, Any]:
    results = [evaluate_criterion(target, c) for c in rubric["criteria"]]
    audit_verdict, unresolved = aggregate(rubric, results)
    if execution_terminal not in {"SUCCEEDED", "FAILED", "INCONCLUSIVE"}:
        execution_terminal = "INCONCLUSIVE"
    result = {
        "schema_version": "audit-result/1",
        "rubric_id": rubric["rubric_id"],
        "execution_terminal": execution_terminal,
        "audit_verdict": audit_verdict,
        "criterion_results": results,
        "unresolved": unresolved,
    }
    return validate_result(result, rubric)
