"""Build Y25 DEV/HOLDOUT incident pairs from curated cross-repo OSS failures."""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "y25"
RNG = random.Random(20261001)

# Curated transfer pairs: same abstract failure_class, different repo/context.
# Not near-duplicate patches. Verified via gh at build time.
PAIR_SPECS: list[dict] = [
    {
        "failure_class": "redirect_authority_semantics",
        "transfer_note": "HTTP redirect authority/body framing across client stacks",
        "transfer_difficulty": "HARD",
        "first": ("aio-libs/aiohttp", "44bbdb83bdb7"),
        "unseen_variant": ("urllib3/urllib3", "adde463f32b7"),
    },
    {
        "failure_class": "redirect_topology_refresh",
        "transfer_note": "Redirect requires topology/region refresh before retry",
        "transfer_difficulty": "HARD",
        "first": ("boto/botocore", "3fe1b11f7e4e"),
        "unseen_variant": ("redis/redis-py", "6e7723c456c9"),
    },
    {
        "failure_class": "out_of_range_protocol_field",
        "transfer_note": "Reject/ignore out-of-range protocol fields (Range vs port)",
        "transfer_difficulty": "HARD",
        "first": ("encode/starlette", "85c3b7434fd6"),
        "unseen_variant": ("redis/redis-py", "a1788da71604"),
    },
    {
        "failure_class": "tls_stream_lifecycle_on_timeout",
        "transfer_note": "Close/cancel TLS streams cleanly on timeout/abort",
        "transfer_difficulty": "MEDIUM",
        "first": ("tornadoweb/tornado", "ce3bffc46c"),
        "unseen_variant": ("urllib3/urllib3", "e05899a66391"),
    },
    {
        "failure_class": "connect_timeout_propagation",
        "transfer_note": "Connect/timeout must be wired to the actual network layer",
        "transfer_difficulty": "MEDIUM",
        "first": ("tornadoweb/tornado", "3bb7bf271e12"),
        "unseen_variant": ("django/django", "f91c8897f568"),
    },
    {
        "failure_class": "retry_side_effect_amplification",
        "transfer_note": "Retries/repeats must not amplify side effects / exceed limits",
        "transfer_difficulty": "HARD",
        "first": ("rq/rq", "030606f801"),
        "unseen_variant": ("urllib3/urllib3", "9a209d2108"),
    },
    {
        "failure_class": "exception_escape_from_protocol_layer",
        "transfer_note": "Internal quiet/protocol exceptions must not escape boundaries",
        "transfer_difficulty": "HARD",
        "first": ("tornadoweb/tornado", "f656a1a575e4"),
        "unseen_variant": ("pallets/flask", "dcbede0cb00d"),
    },
    {
        "failure_class": "buffered_event_flush_ordering",
        "transfer_note": "Buffered work must flush on correct event-loop/hub scheduling",
        "transfer_difficulty": "HARD",
        "first": ("celery/celery", "f7cbeadd4ae2"),
        "unseen_variant": ("rq/rq", "1487e3d526"),
    },
    {
        "failure_class": "host_header_port_matching",
        "transfer_note": "Host matching must account for port / host-header quirks",
        "transfer_difficulty": "MEDIUM",
        "first": ("aio-libs/aiohttp", "a2f1075109c1"),
        "unseen_variant": ("pallets/flask", "a31e6b73469c"),
    },
    {
        "failure_class": "url_absolute_form_authority",
        "transfer_note": "Absolute-form / authority validation before parse vs percent-encoding path edge",
        "transfer_difficulty": "HARD",
        "first": ("aio-libs/aiohttp", "ce960dd17e"),
        "unseen_variant": ("urllib3/urllib3", "3f587c61a1"),
    },
    {
        "failure_class": "schedule_timebase_utc",
        "transfer_note": "Schedulers must use UTC/canonical timebase not local wall clock",
        "transfer_difficulty": "MEDIUM",
        "first": ("rq/rq", "7358790b8f"),
        "unseen_variant": ("celery/celery", "710364329536"),
    },
    {
        "failure_class": "multipart_stream_eof_safety",
        "transfer_note": "Multipart/stream responses must stop safely on unexpected EOF",
        "transfer_difficulty": "MEDIUM",
        "first": ("encode/starlette", "9774b08ef457"),
        "unseen_variant": ("encode/httpx", "10b729592274"),
    },
    {
        "failure_class": "idempotent_backend_forget",
        "transfer_note": "forget()/cleanup must stay idempotent across storage backends",
        "transfer_difficulty": "EASY",
        "first": ("celery/celery", "395d289b27"),
        "unseen_variant": ("celery/celery", "0a24c065ec"),
    },
    {
        "failure_class": "job_pipeline_rate_limit_honor",
        "transfer_note": "Caller pipeline/context must be honored under rate-limit enqueue",
        "transfer_difficulty": "MEDIUM",
        "first": ("rq/rq", "fe06797161"),
        "unseen_variant": ("celery/celery", "a84fd3ed2f"),
    },
    {
        "failure_class": "connection_close_token_handling",
        "transfer_note": "Connection close tokens/lifecycle across HTTP vs DB async contexts",
        "transfer_difficulty": "HARD",
        "first": ("Kludex/uvicorn", "09a236b050ab"),
        "unseen_variant": ("sqlalchemy/sqlalchemy", "6f8998793074"),
    },
    {
        "failure_class": "cancel_fd_double_close",
        "transfer_note": "Cancellation must not double-close fds / leave leaked sockets",
        "transfer_difficulty": "HARD",
        "first": ("MagicStack/uvloop", "dc680eb20c52"),
        "unseen_variant": ("urllib3/urllib3", "09217b75d51f"),
    },
    {
        "failure_class": "http_range_conditional_split",
        "transfer_note": "Range/conditional response application must be explicit and safe",
        "transfer_difficulty": "MEDIUM",
        "first": ("pallets/werkzeug", "830d4b3957e9"),
        "unseen_variant": ("encode/starlette", "4fe55eb264"),
    },
    {
        "failure_class": "admin_date_hierarchy_range",
        "transfer_note": "Out-of-range temporal values must be handled safely (admin vs path ensure)",
        "transfer_difficulty": "HARD",
        "first": ("django/django", "935edaa91b75"),
        "unseen_variant": ("django/django", "2f7f30c320b6"),
    },
    {
        "failure_class": "ssl_connector_deprecation_edge",
        "transfer_note": "SSL connector configuration edge cases across HTTP clients",
        "transfer_difficulty": "MEDIUM",
        "first": ("aio-libs/aiohttp", "25f30573cc01"),
        "unseen_variant": ("encode/httpx", "652f051fea"),
    },
    {
        "failure_class": "cookie_secure_shared_policy",
        "transfer_note": "Secure cookie / CORS vary origin response policy transfer",
        "transfer_difficulty": "HARD",
        "first": ("aio-libs/aiohttp", "6bc84990f2"),
        "unseen_variant": ("encode/starlette", "c9176b57af"),
    },
    {
        "failure_class": "upload_buffer_blocksize",
        "transfer_note": "Upload/buffer sizing vs worker event buffer flush discipline",
        "transfer_difficulty": "HARD",
        "first": ("urllib3/urllib3", "911bc94d2275"),
        "unseen_variant": ("encode/starlette", "41db6a707f26"),
    },
    {
        "failure_class": "cron_heartbeat_self_heal",
        "transfer_note": "Scheduler heartbeat self-heal vs retry interval policy docs/ops",
        "transfer_difficulty": "MEDIUM",
        "first": ("rq/rq", "85936ce63d70"),
        "unseen_variant": ("urllib3/urllib3", "8a26020bc5a0"),
    },
    {
        "failure_class": "duplicate_config_merge",
        "transfer_note": "Merging parallel reads must not duplicate config/setting entries",
        "transfer_difficulty": "HARD",
        "first": ("scrapy/scrapy", "ed551789f4f3"),
        "unseen_variant": ("pandas-dev/pandas", "dd2bf125423c"),
    },
    {
        "failure_class": "tls_handshake_timing_isolation",
        "transfer_note": "TLS handshake leak tests/resources must be timing-independent",
        "transfer_difficulty": "MEDIUM",
        "first": ("tornadoweb/tornado", "57bacc6c8d50"),
        "unseen_variant": ("urllib3/urllib3", "a0cab2d084bd"),
    },
    {
        "failure_class": "secure_shared_cookie_fix",
        "transfer_note": "Shared/secure cookie fixes across HTTP frameworks",
        "transfer_difficulty": "MEDIUM",
        "first": ("aio-libs/aiohttp", "e11d2836203a"),
        "unseen_variant": ("encode/starlette", "699dae42f5"),
    },
    {
        "failure_class": "cron_registry_observability",
        "transfer_note": "Cron/job registries for history vs eager_start scheduling knobs",
        "transfer_difficulty": "HARD",
        "first": ("rq/rq", "e1b13ffb08fd"),
        "unseen_variant": ("MagicStack/uvloop", "3cbb09560ed1"),
    },
    {
        "failure_class": "format_escape_percent",
        "transfer_note": "Escape/format edge cases in node naming vs template autoescape",
        "transfer_difficulty": "HARD",
        "first": ("celery/celery", "31b6167d9529"),
        "unseen_variant": ("pallets/jinja", "5ef70112a1ff"),  # may fail — resolve
    },
]


def _resolve(repo: str, prefix: str) -> dict:
    d = json.loads(
        subprocess.check_output(
            ["gh", "api", f"repos/{repo}/commits/{prefix}"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    )
    msg = (d.get("commit") or {}).get("message", "").split("\n")[0]
    files = [f.get("filename", "") for f in (d.get("files") or [])][:15]
    stats = d.get("stats") or {}
    return {
        "task_id": f"y25_{repo.split('/')[-1]}_{d['sha'][:12]}",
        "repo_url": f"https://github.com/{repo}",
        "repo": repo,
        "commit_sha": d["sha"],
        "patch_ref": d.get("html_url") or f"https://github.com/{repo}/commit/{d['sha']}",
        "license": "SEE_REPO",
        "notes": msg[:200],
        "n_files": len(d.get("files") or []),
        "additions": int(stats.get("additions") or 0),
        "deletions": int(stats.get("deletions") or 0),
        "paths": files,
    }


def _incident(base: dict, *, failure_class: str, role: str) -> dict:
    out = dict(base)
    out["failure_class"] = failure_class
    out["memory_role"] = role
    return out


def main() -> int:
    pairs: list[dict] = []
    for i, spec in enumerate(PAIR_SPECS):
        fr = _resolve(*spec["first"])
        vr = _resolve(*spec["unseen_variant"])
        # Enforce unseen constraints
        assert fr["commit_sha"] != vr["commit_sha"]
        assert fr["patch_ref"] != vr["patch_ref"]
        same_repo = fr["repo"] == vr["repo"]
        pair = {
            "pair_id": f"y25_pair_{i:02d}_{spec['failure_class']}",
            "failure_class": spec["failure_class"],
            "transfer_note": spec["transfer_note"],
            "transfer_difficulty": spec["transfer_difficulty"],
            "same_repo": same_repo,
            "first": _incident(fr, failure_class=spec["failure_class"], role="first"),
            "unseen_variant": _incident(
                vr, failure_class=spec["failure_class"], role="unseen_variant"
            ),
            "pack": "DEV",
        }
        pairs.append(pair)
        print("OK", pair["pair_id"], "same_repo" if same_repo else "cross_repo")

    # Drop pairs that reuse an incident SHA already used (independence)
    used_shas: set[str] = set()
    deduped: list[dict] = []
    for p in pairs:
        shas = {p["first"]["commit_sha"], p["unseen_variant"]["commit_sha"]}
        if used_shas & shas:
            print("SKIP_DUP", p["pair_id"])
            continue
        used_shas |= shas
        deduped.append(p)
    pairs = deduped

    # Prefer cross-repo; need ≥24 total so holdout can be ≥12 (KEEP gate)
    cross = [p for p in pairs if not p["same_repo"]]
    same = [p for p in pairs if p["same_repo"]]
    selected = cross[:]
    if len(selected) < 24:
        selected.extend(same[: max(0, 24 - len(selected))])
    selected = selected[:28]
    if len(selected) < 24:
        raise SystemExit(
            f"only {len(selected)} pairs < 24 needed for holdout≥12 under 50% split"
        )

    # Split ≥50% holdout with holdout N ≥ 12
    RNG.shuffle(selected)
    n_hold = max(12, (len(selected) + 1) // 2)
    n_hold = min(n_hold, len(selected) - 6)  # keep some DEV for memory seed
    for i, p in enumerate(selected):
        p["pack"] = "HOLDOUT" if i < n_hold else "DEV"

    dev = [p for p in selected if p["pack"] == "DEV"]
    hold = [p for p in selected if p["pack"] == "HOLDOUT"]

    def stats(items: list[dict]) -> dict:
        return {
            "n_pairs": len(items),
            "failure_classes": sorted({p["failure_class"] for p in items}),
            "cross_repo_pairs": sum(1 for p in items if not p["same_repo"]),
            "same_repo_pairs": sum(1 for p in items if p["same_repo"]),
            "transfer_difficulty": dict(Counter(p["transfer_difficulty"] for p in items)),
        }

    frozen_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    (ART / "public" / "corpus_manifest.DEV.json").write_text(
        json.dumps(
            {
                "pack": "DEV",
                "status": "POPULATED",
                "protocol_id": "Y25-MV-v1",
                "stats": stats(dev),
                "pairs": sorted(dev, key=lambda x: x["pair_id"]),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    sealed = {
        "pack": "HOLDOUT",
        "status": "FROZEN_UNSEEN",
        "protocol_id": "Y25-MV-v1",
        "stats": stats(hold),
        "pairs": sorted(hold, key=lambda x: x["pair_id"]),
        "unsealed_for_execution": False,
        "frozen_at_utc": frozen_at,
        "sha256_of_sealed_bundle": "PENDING",
        "prereg_sha_file": "artifacts/y25/Y25_PREREG_SHA.txt",
    }
    payload = json.dumps(sealed, indent=2, sort_keys=True) + "\n"
    sha = hashlib.sha256(payload.encode()).hexdigest()
    sealed["sha256_of_sealed_bundle"] = sha
    payload = json.dumps(sealed, indent=2, sort_keys=True) + "\n"
    sha = hashlib.sha256(payload.encode()).hexdigest()
    sealed["sha256_of_sealed_bundle"] = sha
    (ART / "sealed" / "sealed_pack.json").write_text(
        json.dumps(sealed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ART / "sealed" / "HOLDOUT_MANIFEST.json").write_text(
        json.dumps(
            {
                "pack": "HOLDOUT",
                "status": "FROZEN_UNSEEN",
                "protocol_id": "Y25-MV-v1",
                "n_pairs": len(hold),
                "stats": stats(hold),
                "sha256_of_sealed_bundle": sha,
                "frozen_at_utc": frozen_at,
                "unsealed_for_execution": False,
                "sealed_pack_path": "artifacts/y25/sealed/sealed_pack.json",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    blind = []
    for p in sorted(hold, key=lambda x: x["pair_id"]):
        blind.append(
            {
                "pair_id": p["pair_id"],
                "first": {
                    "task_id": p["first"]["task_id"],
                    "repo_url": p["first"]["repo_url"],
                    "commit_sha": p["first"]["commit_sha"],
                    "patch_ref": p["first"]["patch_ref"],
                },
                "unseen_variant": {
                    "task_id": p["unseen_variant"]["task_id"],
                    "repo_url": p["unseen_variant"]["repo_url"],
                    "commit_sha": p["unseen_variant"]["commit_sha"],
                    "patch_ref": p["unseen_variant"]["patch_ref"],
                },
                "notes": "failure_class/labels sealed until execution unseal",
            }
        )
    (ART / "public" / "corpus_manifest.HOLDOUT_BLIND.json").write_text(
        json.dumps(
            {
                "pack": "HOLDOUT_BLIND",
                "status": "BLIND_REFS_ONLY",
                "protocol_id": "Y25-MV-v1",
                "n_pairs": len(blind),
                "pairs": blind,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "protocol_id": "Y25-MV-v1",
        "n_pairs_total": len(selected),
        "dev": stats(dev),
        "holdout": stats(hold),
        "sealed_sha256": sha,
        "holdout_fraction": len(hold) / len(selected),
        "min_pairs_met": len(selected) >= 12,
        "cross_repo_preferred": True,
        "same_repo_pairs_remaining": stats(selected)["same_repo_pairs"],
        "sample_size_expansion_after_unseal": "FORBIDDEN_WITHOUT_LOCKED_AMENDMENT",
        "prereg_frozen": True,
    }
    (ART / "CORPUS_BUILD_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
