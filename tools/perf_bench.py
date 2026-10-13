#!/usr/bin/env python3
"""Reproducible hot-path microbenchmarks for Global OS.

Usage:
  PYTHONPATH=src python3 tools/perf_bench.py --out artifacts/perf/run.json
  PYTHONPATH=src python3 tools/perf_bench.py --compare artifacts/perf/baseline.json \\
      --out artifacts/perf/after.json

Does not claim production throughput; measures local CPU/sqlite micro paths.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _bench(fn: Callable[[], None], n: int, warmup: int = 15) -> dict[str, float]:
    for _ in range(min(warmup, n)):
        fn()
    samples: list[float] = []
    # timed loop as one sample for stable rates; also per-iter mean via total/n
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    total = time.perf_counter() - t0
    # collect a few chunk samples for stdev
    chunk = max(1, n // 8)
    left = n
    while left > 0:
        c = min(chunk, left)
        t1 = time.perf_counter()
        for _ in range(c):
            fn()
        samples.append((time.perf_counter() - t1) / c)
        left -= c
    per = total / n
    return {
        "n": float(n),
        "total_s": total,
        "per_s": per,
        "per_us": per * 1e6,
        "rate_per_s": n / total if total else 0.0,
        "stdev_us": statistics.pstdev(samples) * 1e6 if len(samples) > 1 else 0.0,
    }


def run_suite() -> dict[str, Any]:
    from global_os.common.hashing import content_hash
    from global_os.contracts.validate import validate
    from global_os.kernel.authority.durable_gate import SqliteDurableGateStore
    from global_os.kernel.authority.execution_token import ExecutionTokenService
    from global_os.runtime.events.ledger import EventLedger
    from global_os.verification.completion_gate import evaluate_goal_completion

    payload = {"a": 1, "b": ["x"] * 20, "nested": {f"k{i}": i for i in range(50)}}
    results: dict[str, Any] = {}

    results["content_hash"] = _bench(lambda: content_hash(payload), 4000)

    ledger0 = EventLedger()
    sample = ledger0.append(
        event_type="null_result.recorded",
        tenant_id="t",
        workspace_id="w",
        payload={"i": 1},
        producer="bench",
    )
    ev = dict(sample)
    results["validate_event"] = _bench(lambda: validate(ev, "event.schema.json"), 2500)

    receipt = {
        "receipt_id": "er_0123456789abcdef",
        "schema_version": "0.1.0",
        "action_id": "act_1",
        "tool_response": {"success": True},
        "intended_effect": "page_fetched",
        "observed_effect": "page_fetched",
        "discrepancy": "none",
        "verified_at": "2020-01-01T00:00:00+00:00",
        "verification_method": "trusted_observation",
        "reconciliation_status": "RECONCILED",
        "world_success": True,
    }
    results["validate_effect_receipt"] = _bench(
        lambda: validate(receipt, "effect_receipt.schema.json"), 2500
    )

    ledger = EventLedger()
    results["ledger_append"] = _bench(
        lambda: ledger.append(
            event_type="null_result.recorded",
            tenant_id="t",
            workspace_id="w",
            payload={"i": 1, "blob": "y" * 32},
            producer="bench",
        ),
        900,
    )

    big = EventLedger()
    for i in range(200):
        big.append(
            event_type="null_result.recorded",
            tenant_id="t",
            workspace_id="w",
            payload={"i": i, "s": "x" * 20},
            producer="bench",
        )
    results["ledger_list_events_200"] = _bench(lambda: big.list_events(), 250)

    tok = ExecutionTokenService()
    base = {
        "proposal_id": "ap_1",
        "schema_version": "0.1.0",
        "principal_id": "p1",
        "goal_id": "g1",
        "capability": "web.read",
        "resource": "https://x",
        "intended_effect": "page_fetched",
        "maximum_effect": "page_fetched",
        "reversible": True,
        "information_disclosure": "none",
        "monetary_cost": 0,
        "evidence_refs": [],
        "approval_refs": [],
        "context": {},
    }
    c = {"n": 0}

    def mint_consume() -> None:
        c["n"] += 1
        p = {**base, "idempotency_key": f"idem-{c['n']}"}
        m = tok.mint(proposal=p, proposal_hash=content_hash(p))
        tok.verify_and_consume(m.bearer, proposal=p)

    results["execution_token_mint_consume"] = _bench(mint_consume, 900)

    goal = {
        "goal_id": "g",
        "success_criteria": [{"id": "sc1"}, {"id": "sc2"}],
        "invariants": [],
    }
    receipts = [
        {
            "binds_criteria": ["sc1"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "intended_effect": "a",
            "observed_effect": "a",
            "tool_response": {"success": True},
        },
        {
            "binds_criteria": ["sc2"],
            "reconciliation_status": "RECONCILED",
            "world_success": True,
            "intended_effect": "b",
            "observed_effect": "b",
            "tool_response": {"success": True},
        },
    ]
    results["completion_gate"] = _bench(
        lambda: evaluate_goal_completion(goal=goal, effect_receipts=receipts), 3000
    )

    db = Path(tempfile.mkdtemp()) / "gate.sqlite"
    store = SqliteDurableGateStore(db)
    d = {"n": 0}

    def durable_ops() -> None:
        d["n"] += 1
        jti = f"jti-{d['n']}"
        key = f"idem-{d['n']}"
        store.consume_jti(jti)
        store.claim_idempotency(key)
        store.put_idempotent_receipt(key, {"ok": True, "n": d["n"]})
        store.get_idempotent_receipt(key)

    results["durable_gate_claim_put_get"] = _bench(durable_ops, 350)
    store.close()

    # Composite: weighted wall estimate (relative cost units)
    weights = {
        "ledger_append": 40,
        "ledger_list_events_200": 15,
        "validate_event": 15,
        "durable_gate_claim_put_get": 20,
        "execution_token_mint_consume": 5,
        "completion_gate": 3,
        "content_hash": 2,
    }
    composite = 0.0
    for name, w in weights.items():
        composite += results[name]["per_s"] * w
    results["_composite"] = {
        "weighted_cost_s": composite,
        "weights": weights,
        "note": "Lower is better. Relative microbenchmark mix, not production QPS.",
    }
    return results


def compare(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, cur in current.items():
        if key.startswith("_") or key not in baseline:
            continue
        if not isinstance(cur, dict) or "per_s" not in cur:
            continue
        base = baseline[key]["per_s"]
        speedup = base / cur["per_s"] if cur["per_s"] else float("inf")
        improvement_pct = (1.0 - cur["per_s"] / base) * 100.0 if base else 0.0
        out[key] = {
            "baseline_per_us": baseline[key]["per_us"],
            "current_per_us": cur["per_us"],
            "speedup_x": speedup,
            "improvement_pct": improvement_pct,
        }
    if "_composite" in baseline and "_composite" in current:
        b = baseline["_composite"]["weighted_cost_s"]
        c = current["_composite"]["weighted_cost_s"]
        out["_composite"] = {
            "baseline_weighted_cost_s": b,
            "current_weighted_cost_s": c,
            "speedup_x": b / c if c else float("inf"),
            "improvement_pct": (1.0 - c / b) * 100.0 if b else 0.0,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--compare", type=Path, default=None)
    args = ap.parse_args()

    suite = run_suite()
    doc = {
        "meta": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cwd": str(ROOT),
            "gos_profile": os.environ.get("GOS_PROFILE", "dev"),
            "integration_sha_hint": "see git rev-parse HEAD",
        },
        "results": suite,
    }
    if args.compare and args.compare.exists():
        base_doc = json.loads(args.compare.read_text(encoding="utf-8"))
        doc["compare"] = compare(base_doc.get("results") or base_doc, suite)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {args.out}")
    for k, v in suite.items():
        if k.startswith("_"):
            continue
        print(f"  {k:32s} {v['per_us']:9.1f} µs/op  ({v['rate_per_s']:.0f}/s)")
    print(f"  COMPOSITE weighted_cost_s={suite['_composite']['weighted_cost_s']:.6f}")
    if "compare" in doc and "_composite" in doc["compare"]:
        c = doc["compare"]["_composite"]
        print(
            f"  vs baseline: {c['improvement_pct']:.1f}% faster "
            f"({c['speedup_x']:.2f}x) composite"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
