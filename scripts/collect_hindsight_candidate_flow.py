#!/usr/bin/env python3
"""Capture Hindsight's native trace candidate flow for the stress corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hindsight_client import Hindsight

from memory_bakeoff.corpus import build_corpus


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--bank", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    _, cases = build_corpus(distractors=450)
    client = Hindsight(base_url=args.url)
    rows = []
    try:
        for case in cases:
            response = client.recall(bank_id=args.bank, query=case.query, max_tokens=4096, trace=True)
            trace = response.trace or {}
            native_docs = {result.id: result.document_id for result in response.results if result.document_id}
            arms: dict[str, dict[str, int]] = {}
            for arm in trace.get("retrieval_results", []):
                name = arm["method_name"]
                for candidate in arm.get("results", []):
                    doc_id = native_docs.get(candidate["node_id"])
                    if doc_id:
                        arms.setdefault(doc_id, {})[name] = candidate["rank"]
            rrf = {
                native_docs[candidate["node_id"]]: {
                    "rank": candidate["final_rrf_rank"],
                    "source_ranks": candidate["source_ranks"],
                }
                for candidate in trace.get("rrf_merged", [])
                if candidate["node_id"] in native_docs
            }
            final = {
                native_docs[candidate["node_id"]]: {
                    "rank": candidate["rerank_rank"],
                    "rrf_rank": candidate["rrf_rank"],
                    "rank_change": candidate["rank_change"],
                }
                for candidate in trace.get("reranked", [])
                if candidate["node_id"] in native_docs
            }
            relevant = list(case.relevant_ids)
            rows.append({
                "case_id": case.id,
                "relevant_ids": relevant,
                "prohibited_ids": list(case.prohibited_ids),
                "top5_document_ids": [result.document_id for result in response.results[:5]],
                "relevant_candidate_flow": {
                    record_id: {"arms": arms.get(record_id), "rrf": rrf.get(record_id), "final": final.get(record_id)}
                    for record_id in relevant
                },
                "trace_candidate_counts": {
                    name: sum(1 for arm in trace.get("retrieval_results", []) if arm["method_name"] == name for _ in arm.get("results", []))
                    for name in ("semantic", "bm25", "graph", "temporal")
                },
            })
    finally:
        client.close()
    Path(args.out).parent.mkdir(parents=True, exist_ok=False)
    Path(args.out).write_text(json.dumps({"bank": args.bank, "rows": rows}, indent=2) + "\n")


if __name__ == "__main__":
    main()
