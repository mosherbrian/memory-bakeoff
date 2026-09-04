#!/usr/bin/env python
"""Gen40: reproduce MemBukkit's previously blocked intended-model path.

No score. No benchmark corpus. No reader, no external LLM, no GPU server.
Phase ``online`` acquires and pins the two MemseekAI repositories and runs the
synthetic preflight; it then re-execs itself as phase ``offline`` with outbound
network blocked, so "it ran from the frozen local snapshot" is proved rather
than asserted.

    python scripts/run_membukkit_gen40_preflight.py --out results/membukkit_gen40_intended_model
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import (  # noqa: E402
    INTENDED_ENCODER_REPO,
    INTENDED_RERANKER_REPO,
    MEMBUKKIT_PINNED_COMMIT,
    PROBE_QUERY,
    PROBE_TEXTS,
    SUBJECT,
    SYNTHETIC_FACTS,
    SYNTHETIC_QUERIES,
    block_network,
    contract_sha256,
    leaf_digest,
    reconcile_snapshot,
    snapshot_identity,
    trace_loads,
)


def membukkit_source_identity() -> dict:
    import membukkit

    checkout = Path(membukkit.__file__).resolve().parents[2]
    head = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    registry = checkout / "src" / "membukkit" / "models" / "registry.py"
    lines = registry.read_text().splitlines()
    resolver_lines = {
        n + 1: line
        for n, line in enumerate(lines)
        if "_HUB_ENCODER_REPO" in line or "_HUB_RERANKER_REPO" in line
        or "_FALLBACK_ENCODER" in line or "_FALLBACK_RERANKER" in line
    }
    return {
        "checkout": str(checkout),
        "head": head,
        "matches_gen7_pin": head == MEMBUKKIT_PINNED_COMMIT,
        "version": getattr(membukkit, "__version__", ""),
        "resolver_file": str(registry.relative_to(checkout)),
        "resolver_lines": resolver_lines,
    }


def remote_revision(repo: str) -> dict:
    """Pin a repo to an exact revision and per-file content identity."""
    from huggingface_hub import HfApi

    info = HfApi().model_info(repo, files_metadata=True)
    files = {}
    for s in info.siblings:
        lfs = getattr(s, "lfs", None)
        files[s.rfilename] = {
            "size": getattr(s, "size", None),
            "oid": getattr(s, "blob_id", None),
            "lfs_sha256": (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None,
        }
    card = info.cardData or {}
    return {
        "repo": repo,
        "revision": info.sha,
        "private": bool(getattr(info, "private", False)),
        "gated": getattr(info, "gated", False),
        "library_name": getattr(info, "library_name", None),
        "pipeline_tag": getattr(info, "pipeline_tag", None),
        "license": card.get("license"),
        "files": files,
    }


def build_system():
    """Construct the product on its own intended path, with no reader LLM."""
    from membukkit import ModelConfig, MemorySystem

    # A local spec that is never called: this generation exercises ingest_facts
    # and search only, both of which are LLM-free. Any call raises.
    system = MemorySystem.from_pretrained(
        models=ModelConfig(device="cpu"),
        llm="local:http://127.0.0.1:1/v1:unused",
    )
    calls = {"n": 0}

    def refuse(*a, **kw):
        calls["n"] += 1
        raise AssertionError("Gen40 must not call an LLM")

    for attr in ("_llm_fn", "_distiller"):
        if hasattr(system, attr):
            setattr(system, attr, refuse)
    return system, calls


def probe_models(system) -> dict:
    """Check 1 and 2: both intended models load and produce finite output."""
    import numpy as np

    emb = system._encoder.encode(list(PROBE_TEXTS))
    scores = system._reranker.score(PROBE_QUERY, list(PROBE_TEXTS))
    emb = np.asarray(emb, dtype=np.float64)
    scores = np.asarray(scores, dtype=np.float64)
    return {
        "encoder_shape": list(emb.shape),
        "encoder_all_finite": bool(np.isfinite(emb).all()),
        "encoder_first_row_head": [round(float(x), 6) for x in emb[0][:8]],
        "encoder_row_norms": [round(float(np.linalg.norm(r)), 6) for r in emb],
        "reranker_n_scores": int(scores.size),
        "reranker_all_finite": bool(np.isfinite(scores).all()),
        "reranker_scores": [round(float(x), 6) for x in scores],
        "reranker_order": [int(i) for i in np.argsort(scores)[::-1]],
        "encoder_device": str(getattr(system._encoder.model, "device", "")),
        "reranker_device": str(getattr(system._reranker, "device", "")),
    }


def run_searches(system) -> list:
    results = []
    for q in SYNTHETIC_QUERIES:
        res = system.search(q["text"])
        results.append(
            {
                "qid": q["qid"],
                "kind": q["kind"],
                "n_hits": len(res.hits),
                "returned_ids": [h.source_id for h in res.hits],
                "refs": [h.ref for h in res.hits],
                "texts": [h.text for h in res.hits],
                "scan_fraction": round(float(getattr(res.trace, "scan_fraction", 0.0)), 6),
                "n_scanned": int(getattr(res.trace, "n_scanned", 0) or 0),
                "n_facts": int(getattr(res.trace, "n_facts", 0) or 0),
            }
        )
    return results


def lifecycle_probe(system) -> dict:
    """Does the raw intended path mutate state, or is it retrieval-only here?

    Descriptive only: re-offer the identical facts, then offer one dated update
    that contradicts a stored fact, and report what the product does.
    """
    before = system._backend.count()
    n_dup = system.ingest_facts(list(SYNTHETIC_FACTS), subject=SUBJECT)
    after_dup = system._backend.count()
    update = [
        {
            "fact_id": "SYN-UPD-0001",
            "text": "Nell Ardwick now chairs the society, replacing Petra Lindqvist.",
            "timestamp": "2031-09-02",
        }
    ]
    n_upd = system.ingest_facts(update, subject=SUBJECT)
    after_upd = system._backend.count()
    res = system.search("Who chairs the society?", include_history=True)
    return {
        "count_before": int(before),
        "duplicate_offer_new_rows": int(n_dup),
        "count_after_duplicate_offer": int(after_dup),
        "update_offer_new_rows": int(n_upd),
        "count_after_update": int(after_upd),
        "statuses_seen": sorted({str(h.status) for h in res.hits}),
        "n_superseded_hits": sum(1 for h in res.hits if h.superseded_by),
        "n_hits": len(res.hits),
    }


def preflight(phase: str, pins: dict) -> dict:
    from membukkit.storage.base import content_id

    started = time.time()
    source = membukkit_source_identity()
    allowed_roots = [str(Path.home() / ".membukkit" / "models")]
    cache_before = {
        role: (Path(allowed_roots[0]) / repo.replace("/", "__") / "config.json").exists()
        for role, repo in (("encoder", INTENDED_ENCODER_REPO), ("reranker", INTENDED_RERANKER_REPO))
    }

    with trace_loads() as trace:
        system, llm_calls = build_system()
        probes = probe_models(system)

        n_new = system.ingest_facts(list(SYNTHETIC_FACTS), subject=SUBJECT)
        count_after_ingest = int(system._backend.count())
        receipts = {
            content_id(f["fact_id"], SUBJECT): f["fact_id"] for f in SYNTHETIC_FACTS
        }
        first = run_searches(system)
        repeat = run_searches(system)
        lifecycle = lifecycle_probe(system)
        trace.assert_intended_only(allowed_roots)

    snapshots = {}
    for role, repo in (("encoder", INTENDED_ENCODER_REPO), ("reranker", INTENDED_RERANKER_REPO)):
        local_dir = Path(allowed_roots[0]) / repo.replace("/", "__")
        local = snapshot_identity(local_dir)
        entry = {"repo": repo, "local_dir": str(local_dir), "local_files": local}
        if pins.get(role):
            entry["revision"] = pins[role]["revision"]
            entry["reconciliation"] = reconcile_snapshot(local, pins[role]["files"])
        snapshots[role] = entry

    unmapped = sorted(
        {i for r in first for i in r["returned_ids"] if i not in receipts}
    )
    order_stable = all(
        a["returned_ids"] == b["returned_ids"] for a, b in zip(first, repeat)
    )
    set_stable = all(
        set(a["returned_ids"]) == set(b["returned_ids"]) for a, b in zip(first, repeat)
    )

    return {
        "phase": phase,
        "evidence_class": "product_identity_reproduction_no_score",
        "contract_sha256": contract_sha256(),
        "membukkit_source": source,
        "model_pins": pins,
        "snapshot_cached_before_run": cache_before,
        "snapshots": snapshots,
        "load_trace": trace.to_dict(),
        "llm_invocations": llm_calls["n"],
        "ingest": {
            "n_facts_offered": len(SYNTHETIC_FACTS),
            "n_new_written": int(n_new),
            "n_receipts": len(receipts),
            "backend_count": count_after_ingest,
        },
        "probes": probes,
        "retrieval_defaults": {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in vars(system._retrieval).items()
        },
        "lifecycle": lifecycle,
        "searches": first,
        "repeat": repeat,
        "provenance": {
            "unmapped_returned_ids": unmapped,
            "all_returns_mapped": not unmapped,
        },
        "stability": {
            "repeats_order_stable": order_stable,
            "repeats_selection_stable": set_stable,
        },
        "wall_clock_seconds": round(time.time() - started, 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/membukkit_gen40_intended_model")
    ap.add_argument("--phase", choices=["online", "offline"], default="online")
    args = ap.parse_args()

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    if args.phase == "offline":
        block_network()
        pins = json.loads((out / "model_pins.json").read_text())
        leaf = preflight("offline", pins)
        leaf["digest"] = leaf_digest(leaf)
        (out / "offline.json").write_text(json.dumps(leaf, indent=2, sort_keys=True))
        print("offline phase written")
        return 0

    pins = {
        "encoder": remote_revision(INTENDED_ENCODER_REPO),
        "reranker": remote_revision(INTENDED_RERANKER_REPO),
    }
    (out / "model_pins.json").write_text(json.dumps(pins, indent=2, sort_keys=True))

    leaf = preflight("online", pins)
    leaf["digest"] = leaf_digest(leaf)
    (out / "online.json").write_text(json.dumps(leaf, indent=2, sort_keys=True))
    print("online phase written; digest", leaf["digest"][:16])

    env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    proc = subprocess.run(
        [sys.executable, str(Path(__file__)), "--out", args.out, "--phase", "offline"],
        env=env, cwd=str(ROOT),
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
