#!/usr/bin/env python3
"""Gen38: the frozen Gen36 BM25 baseline over the full release, as context only.

Same provider, same allowed-prefix rule and same top-k as the Gen36 pilot; only
the persona set widens. Emits Gen38-schema leaves so the same report builder
scores it. No product, no reader, no LLM, no GPU.
"""
from __future__ import annotations

import argparse, hashlib, json, os, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.models import MemoryRecord, QueryCase
from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.round2_reporting import ReportingError

LEAF_SCHEMA = "memconflict-gen38-leaf-v1"
TOP_K = 5
BASELINE_ID = "bm25-frozen-gen36-baseline"


def leaf_digest(leaf: dict) -> str:
    content = {
        "schema": LEAF_SCHEMA, "engine": leaf["engine"], "persona_id": leaf["persona_id"],
        "adapter_sha256": leaf["adapter_sha256"],
        "questions": [
            {"question_key": r["question_key"],
             "returned_sessions": [i["session_id"] for i in r["returned"]],
             "provenance_status": [i["provenance_status"] for i in r["returned"]]}
            for r in leaf["questions"]],
    }
    return hashlib.sha256(canonical_json(content).encode()).hexdigest()


def baseline_sha256() -> str:
    """Identity of the frozen baseline: the provider source plus its parameters."""
    source = (ROOT / "src/memory_bakeoff/providers/bm25.py").read_bytes()
    payload = {"provider_sha256": hashlib.sha256(source).hexdigest(),
               "k1": 1.5, "b": 0.75, "top_k": TOP_K,
               "unit": "one released dialogue message", "query": "released question text",
               "prefix_rule": "sessions 0..i inclusive"}
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


def run_persona(persona: dict) -> dict:
    units, anomalies = M.parse_dialogue(persona)
    records = []
    started = time.perf_counter()
    for question in M.questions(persona):
        allowed = [u for u in units if u.session_index in M.allowed_session_indices(question)]
        returned = []
        if allowed:
            by_id = {u.provenance_id: u for u in allowed}
            provider = BM25Provider()
            provider.ingest([MemoryRecord(id=u.provenance_id, text=u.text,
                                          timestamp=datetime.fromisoformat(u.date),
                                          session_id=str(u.session_id)) for u in allowed])
            result = provider.retrieve(QueryCase(id=question.key, category="memconflict",
                                                 query=question.text, relevant_ids=()), top_k=TOP_K)
            for rank, item in enumerate(result.items[:TOP_K], start=1):
                unit = by_id.get(item.record_id)
                if unit is None:
                    raise ReportingError(f"{question.key}: baseline returned an unmapped id")
                if unit.session_index > question.session_index:
                    raise ReportingError(f"{question.key}: baseline returned a future session")
                returned.append({"rank": rank, "score": item.score, "provenance_status": "mapped",
                                 "session_id": unit.session_id, "session_index": unit.session_index,
                                 "turn": unit.turn_index, "message": unit.message_index})
        records.append({"question_key": question.key, "question_id": question.question_id,
                        "session_id": question.session_id, "session_index": question.session_index,
                        "returned": returned, "returned_count": len(returned), "latency_ms": None})

    leaf = {
        "schema": LEAF_SCHEMA, "engine": "bm25", "persona_id": persona["ID"],
        "adapter_version": BASELINE_ID, "adapter_sha256": baseline_sha256(),
        "contract_sha256": M.contract_sha256(), "dataset_sha256": M.DATASET_SHA256,
        "upstream_commit": M.UPSTREAM_COMMIT,
        "questions": records, "read_side_effect_audit": [], "deterministic_repeats": [],
        "inventory": {"documents": len(units), "note": "in-memory baseline; no product store"},
        "operations": {"expected_valid_messages": len(units), "malformed_excluded": len(anomalies),
                       "successful_writes": len(units), "distinct_native_ids": len(units),
                       "write_actions": {"in_memory": len(units)}, "quarantined_writes": [],
                       "write_failures": [], "write_latency": {"count": 0},
                       "query_latency": {"count": len(records)},
                       "questions_executed": len(records),
                       "wall_seconds": round(time.perf_counter() - started, 2),
                       "store_bytes": 0, "bytes_per_write": 0.0},
        "ledger_size": len(units),
    }
    leaf["leaf_digest"] = leaf_digest(leaf)
    return leaf


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen38_full_release/bm25"))
    args = ap.parse_args()
    if M.dataset_sha256() != M.DATASET_SHA256:
        raise ReportingError("pinned dataset hash drift; refusing to run")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    personas = M.load_personas()
    for index, persona in enumerate(personas, start=1):
        leaf = run_persona(persona)
        temp = out / f"persona-{persona['ID']}.json.tmp"
        temp.write_text(json.dumps(leaf, indent=2, sort_keys=True) + "\n")
        os.replace(temp, out / f"persona-{persona['ID']}.json")
        print(f"[{index}/{len(personas)}] bm25 {persona['ID'][:12]}: "
              f"{leaf['operations']['questions_executed']} questions, "
              f"{leaf['operations']['wall_seconds']}s, digest {leaf['leaf_digest'][:12]}", flush=True)
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
