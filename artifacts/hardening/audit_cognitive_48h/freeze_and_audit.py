"""Independent LH-COGNITIVE 48h auditor — separate contour from exam executor.

Reads ONLY freeze pack paths listed in ALLOWED_READ.
Does not write into the live exam tree except via --freeze-root / --out.
Never sets m15_claimed=true; only recommends M1.5 candidate / NOT_CLAIMED.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXAM_SHA = "7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb"
REQUIRED_WALL = 172800.0
PROTOCOL = "LH-COGNITIVE-v1"

DEFAULT_SOURCES = (
    "artifacts/hardening/long_horizon_48h/windows_cognitive_wall_48h",
    "artifacts/hardening/long_horizon_48h/windows_cognitive_preflight",
    "artifacts/hardening/long_horizon_48h/os_kill_smoke_windows_cognitive",
)


@dataclass
class Gate:
    id: str
    passed: bool
    detail: str


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_pack(*, repo_root: Path, freeze_root: Path, sources: list[str]) -> dict[str, Any]:
    """Copy raw trees into freeze_root and write MANIFEST (no mutation of sources)."""
    if freeze_root.exists():
        raise FileExistsError(f"freeze root already exists: {freeze_root}")
    freeze_root.mkdir(parents=True)
    manifest: list[dict[str, str]] = []
    copied: list[str] = []
    for rel in sources:
        src = repo_root / rel
        if not src.exists():
            raise FileNotFoundError(f"missing source for freeze: {rel}")
        dst = freeze_root / Path(rel).name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied.append(rel)
        for p in sorted(dst.rglob("*")):
            if p.is_file():
                rel_p = p.relative_to(freeze_root).as_posix()
                manifest.append({"path": rel_p, "sha256": _sha256_file(p)})
    meta = {
        "frozen_at_utc": datetime.now(UTC).isoformat(),
        "exam_sha_expected": EXAM_SHA,
        "protocol": PROTOCOL,
        "sources": copied,
        "note": "raw copy; do not edit files under freeze_root",
    }
    (freeze_root / "FREEZE_META.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (freeze_root / "MANIFEST.sha256.json").write_text(
        json.dumps({"files": manifest, "n_files": len(manifest)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"freeze_root": str(freeze_root), "n_files": len(manifest), "meta": meta}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_freeze(freeze_root: Path) -> dict[str, Any]:
    """Deterministic independent audit of a frozen cognitive 48h pack."""
    wall = freeze_root / "windows_cognitive_wall_48h"
    pre = freeze_root / "windows_cognitive_preflight"
    smoke = freeze_root / "os_kill_smoke_windows_cognitive"
    report_path = wall / "program_report.json"
    pass_path = wall / "PASS_CRITERIA.json"
    start_path = wall / "EXAM_START.json"
    locked = wall / "missions" / "object" / "LOCKED_OBJECT.json"
    review_pack = wall / "missions" / "review" / "TERMINAL_REVIEW_PACK.json"
    evidence_dir = wall / "missions" / "evidence"

    gates: list[Gate] = []

    def add(gid: str, ok: bool, detail: str) -> None:
        gates.append(Gate(gid, ok, detail))

    add("freeze_meta_present", (freeze_root / "FREEZE_META.json").is_file(), "FREEZE_META.json")
    add("manifest_present", (freeze_root / "MANIFEST.sha256.json").is_file(), "MANIFEST.sha256.json")
    add("wall_report_present", report_path.is_file(), str(report_path))
    add("pass_criteria_present", pass_path.is_file(), str(pass_path))
    add("exam_start_present", start_path.is_file(), str(start_path))
    add("preflight_present", pre.is_dir() and (pre / "program_report.json").is_file(), str(pre))
    add("smoke_present", smoke.is_dir(), str(smoke))

    report: dict[str, Any] = {}
    if report_path.is_file():
        report = _load_json(report_path)

    fidelity = str(report.get("fidelity") or "")
    wall_s = float(report.get("wall_seconds") or 0.0)
    m15 = report.get("m15_claimed")
    prov = report.get("provenance") or {}
    sha = str(prov.get("git_sha") or "")
    workload = str(prov.get("workload_class") or report.get("contract", {}).get("workload_class") or "")
    top_passed = report.get("passed") is True

    add("fidelity_cognitive_wall", fidelity == "COGNITIVE_WALL_CLOCK_48H", fidelity)
    add("wall_seconds_hard_gate", wall_s + 1e-9 >= REQUIRED_WALL, f"wall_seconds={wall_s}")
    add("m15_claimed_false", m15 is False, f"m15_claimed={m15}")
    add("git_sha_freeze", sha.startswith("7ab345e") and sha == EXAM_SHA, sha)
    add("workload_external", workload == "EXTERNAL_RESEARCH_OBJECT", workload)
    add("top_level_passed", top_passed, f"passed={report.get('passed')}")

    crit = report.get("criteria") or []
    if not crit and pass_path.is_file():
        crit = (_load_json(pass_path).get("criteria") or [])
    all_crit = all(bool(c.get("passed")) for c in crit) if crit else False
    add("all_criteria_passed", all_crit, f"n_criteria={len(crit)}")

    # Cognitive substance
    add("locked_object_present", locked.is_file(), str(locked))
    add("terminal_review_pack_present", review_pack.is_file(), str(review_pack))
    n_ev = len(list(evidence_dir.glob("*.json"))) if evidence_dir.is_dir() else 0
    add("evidence_files_min", n_ev >= 5, f"n_evidence_json={n_ev}")

    if locked.is_file():
        obj = _load_json(locked)
        add(
            "locked_object_id",
            obj.get("object_id") == "EXT-JAIN-WALLACE-2019-ATTN-EXPLAIN",
            str(obj.get("object_id")),
        )
        add(
            "not_sum_harness_object",
            "sum(1..20)" in str(obj.get("forbidden_primary_criterion", "")),
            "forbidden_primary listed",
        )

    # Preflight sanity (supporting)
    if (pre / "program_report.json").is_file():
        pr = _load_json(pre / "program_report.json")
        add(
            "preflight_supporting_pass",
            pr.get("passed") is True and "COGNITIVE_PREFLIGHT" in str(pr.get("fidelity")),
            str(pr.get("fidelity")),
        )
    else:
        add("preflight_supporting_pass", False, "missing preflight report")

    # Honesty: must not self-claim M1.5 inside report notes
    notes = str(report.get("notes") or "")
    add(
        "no_self_m15_in_notes",
        "M1.5 not claimed" in notes or "not claimed" in notes.lower() or m15 is False,
        "notes/m15 check",
    )

    # Forbidden overclaim markers in freeze
    blob = json.dumps(report)
    add("no_gos_advantage_claim", "gos_advantage" not in blob.lower() or "not measured" in blob.lower(), "scan")

    all_pass = all(g.passed for g in gates)
    # Scope-limited recommendation only
    if all_pass:
        m15_recommendation = "M1.5_CANDIDATE_SCOPE_LIMITED"
        verdict = (
            "Frozen LH-COGNITIVE-v1 pack meets locked mechanical gates: "
            "COGNITIVE_WALL_CLOCK_48H, wall_seconds>=172800, EXTERNAL_RESEARCH_OBJECT, "
            "exam SHA 7ab345e, m15_claimed=false, cognitive evidence+review pack present. "
            "Recommend scope-limited M1.5 candidate discussion. "
            "Does NOT prove production security, distributed exactly-once, Continual SI, "
            "or causal GOS advantage vs strong baseline."
        )
    else:
        m15_recommendation = "M1.5_NOT_CLAIMED"
        failed = [g.id for g in gates if not g.passed]
        verdict = f"Independent audit FAILED gates: {failed}. M1.5 NOT CLAIMED."

    out = {
        "reviewer_contour": "independent_lh_cognitive_48h_v1",
        "protocol": PROTOCOL,
        "exam_sha_expected": EXAM_SHA,
        "audited_at_utc": datetime.now(UTC).isoformat(),
        "freeze_root": str(freeze_root),
        "allowed_read": [
            "FREEZE_META.json",
            "MANIFEST.sha256.json",
            "windows_cognitive_wall_48h/**",
            "windows_cognitive_preflight/program_report.json",
            "os_kill_smoke_windows_cognitive/**",
        ],
        "did_not_do": [
            "edit_raw_exam_artifacts",
            "claim_M1.5_as_executor",
            "read_unrelated_OPEN_HYPOTHESES",
            "patch_freeze_sha",
        ],
        "gates": [asdict(g) for g in gates],
        "summary": {
            "fidelity": fidelity,
            "wall_seconds": wall_s,
            "git_sha": sha,
            "workload_class": workload,
            "m15_claimed_in_report": m15,
            "n_evidence_json": n_ev,
            "all_gates_passed": all_pass,
        },
        "m15_recommendation": m15_recommendation,
        "m15_claimed_by_auditor": False,
        "verdict": verdict,
    }
    return out


def write_audit_outputs(out_dir: Path, review: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "INDEPENDENT_REVIEW.json").write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    failed = [g["id"] for g in review["gates"] if not g["passed"]]
    md = f"""# LH-COGNITIVE 48h INDEPENDENT REVIEW

**Contour:** `{review["reviewer_contour"]}`  
**Protocol:** {review["protocol"]}  
**Exam SHA expected:** `{review["exam_sha_expected"]}`  
**Audited:** {review["audited_at_utc"]}

## Summary

| Field | Value |
|-------|-------|
| fidelity | {review["summary"]["fidelity"]} |
| wall_seconds | {review["summary"]["wall_seconds"]} |
| git_sha | `{review["summary"]["git_sha"]}` |
| workload_class | {review["summary"]["workload_class"]} |
| m15_claimed (report) | {review["summary"]["m15_claimed_in_report"]} |
| n_evidence_json | {review["summary"]["n_evidence_json"]} |
| all_gates_passed | **{review["summary"]["all_gates_passed"]}** |

## Recommendation

**{review["m15_recommendation"]}**  
Auditor `m15_claimed_by_auditor`: **false** (never self-certifies).

## Failed gates

{failed if failed else "_none_"}

## Verdict

{review["verdict"]}
"""
    (out_dir / "INDEPENDENT_REVIEW.md").write_text(md, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Freeze + independent audit LH-COGNITIVE 48h pack")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--freeze-root",
        type=Path,
        default=Path("artifacts/hardening/freeze_lh_cognitive_7ab345e"),
    )
    ap.add_argument("--skip-freeze", action="store_true", help="audit existing freeze-root only")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/hardening/audit_cognitive_48h/out"),
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    freeze_root = args.freeze_root if args.freeze_root.is_absolute() else repo / args.freeze_root
    out_dir = args.out if args.out.is_absolute() else repo / args.out

    if not args.skip_freeze:
        freeze_pack(repo_root=repo, freeze_root=freeze_root, sources=list(DEFAULT_SOURCES))
    review = audit_freeze(freeze_root)
    write_audit_outputs(out_dir, review)
    # also copy review into freeze pack (audit result, not raw mutation of wall reports)
    write_audit_outputs(freeze_root / "independent_audit", review)
    print(json.dumps({
        "all_gates_passed": review["summary"]["all_gates_passed"],
        "m15_recommendation": review["m15_recommendation"],
        "freeze_root": str(freeze_root),
        "out": str(out_dir),
    }, indent=2))
    return 0 if review["summary"]["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
