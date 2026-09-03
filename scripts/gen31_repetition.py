#!/usr/bin/env python3
"""One Gen31 repetition: ingest the frozen prefix, capture checkpoints, run the 20 cases."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import hindsight_longitudinal as H

LIMIT = 5


def sql(pgbin: str, db: str, query: str) -> str:
    """Raise on a failed query. A broken query must never look like an empty result."""
    done = subprocess.run([f"{pgbin}/psql", "-h", "127.0.0.1", "-d", db, "-Atc", query],
                          text=True, capture_output=True, timeout=60)
    if done.returncode != 0:
        raise SystemExit(f"state query failed ({done.returncode}): {query}\n{done.stderr.strip()[:300]}")
    return done.stdout.strip()


def result_rows(raw, native_to_canonical):
    got = getattr(raw, "results", None)
    if got is None and isinstance(raw, dict):
        got = raw.get("results") or []
    items = []
    for rank, x in enumerate(list(got or [])[:LIMIT], start=1):
        get = (lambda k: x.get(k)) if isinstance(x, dict) else (lambda k: getattr(x, k, None))
        scores = get("scores")
        if scores is not None and not isinstance(scores, dict):
            scores = {k: v for k, v in vars(scores).items() if not k.startswith("_")}
        metadata = get("metadata") or {}
        document_id = get("document_id")
        marker = metadata.get("record_id") if isinstance(metadata, dict) else None
        canonical = native_to_canonical.get(document_id)
        exact = canonical is not None and marker == canonical
        items.append({"native_rank": rank, "document_id": document_id, "chunk_id": get("chunk_id"),
                      "canonical_id": canonical if exact else None, "provenance_exact": exact,
                      "text": (get("text") or "")[:120], "mentioned_at": get("mentioned_at"),
                      "occurred_start": get("occurred_start"), "scores": scores})
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--bank", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--pgbin", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from hindsight_client import Hindsight

    if L.fixture_sha256() != "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd":
        raise SystemExit("longitudinal-v1 fixture hash drift; refusing to run")
    if L.scorer_contract_sha256() != "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34":
        raise SystemExit("longitudinal scorer contract hash drift; refusing to run")

    fixture = L.build_longitudinal_fixture()
    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")
    checkpoints = {c.ingestion_order: c for c in fixture.checkpoints}
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    native_to_canonical: dict[str, str] = {}
    records: list[dict] = []
    checkpoint_state: dict[str, dict] = {}
    lifecycle_by_checkpoint: dict[str, list] = {}

    for observation in fixture.observations:
        payload = H.retain_arguments(observation, args.bank)
        H.assert_public_only(payload)
        client.retain(**payload)
        native_to_canonical[payload["document_id"]] = observation.id
        time.sleep(0.05)

        checkpoint = checkpoints.get(observation.ingestion_order)
        if checkpoint is None:
            continue

        prefix_ids = {o.id for o in fixture.prefix(checkpoint.id)}
        state = {
            "documents": sql(args.pgbin, args.db, "select count(*) from documents"),
            "memory_units": sql(args.pgbin, args.db, "select count(*) from memory_units"),
            "chunks": sql(args.pgbin, args.db, "select count(*) from chunks"),
            "memory_links": sql(args.pgbin, args.db, "select count(*) from memory_links"),
            "entities": sql(args.pgbin, args.db, "select count(*) from entities"),
            # curation state is a side table in this schema, not a column on memory_units
            "invalidated": sql(args.pgbin, args.db, "select count(*) from invalidated_memory_units"),
        }
        checkpoint_state[checkpoint.id] = state
        # document_id lives on memory_units, not documents; the marker is record-<canonical id>
        present = sql(args.pgbin, args.db,
                      "select string_agg(distinct document_id, ',') from memory_units "
                      "where document_id is not null")
        present_ids = {p for p in (present or "").split(",") if p}
        expected_ids = {H.document_id_for(o.id) for o in fixture.prefix(checkpoint.id)}
        if not expected_ids <= present_ids:
            raise SystemExit(
                f"lifecycle membership check failed at {checkpoint.id}: "
                f"missing {sorted(expected_ids - present_ids)}; saw {sorted(present_ids)[:4]}")
        lifecycle_by_checkpoint[checkpoint.id] = [
            L.LifecycleEvidence(canonical_id,
                                active_current=H.document_id_for(canonical_id) in present_ids,
                                historically_recoverable=True if H.document_id_for(canonical_id) in present_ids else None,
                                disposition=L.LifecycleDisposition.ACTIVE_CURRENT if H.document_id_for(canonical_id) in present_ids else L.LifecycleDisposition.UNKNOWN,
                                evidence_strength="native_document_row",
                                native_evidence=f"documents row present={H.document_id_for(canonical_id) in present_ids}")
            for canonical_id in sorted(prefix_ids)]

        prefix_sha = hashlib.sha256(L.canonical_json([o.public_dict() for o in fixture.prefix(checkpoint.id)]).encode()).hexdigest()
        for case in cases_by_checkpoint.get(checkpoint.id, []):
            arguments = H.recall_arguments(case, args.bank, LIMIT)
            started = time.perf_counter()
            raw = client.recall(**arguments)
            latency_ms = (time.perf_counter() - started) * 1000
            items = result_rows(raw, native_to_canonical)
            trace = getattr(raw, "trace", None)
            records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                            "ingested_prefix_sha256": prefix_sha,
                            "native_temporal_operation": H.native_operation(case),
                            "query_timestamp": arguments.get("query_timestamp"),
                            "requested_limit": LIMIT, "latency_ms": round(latency_ms, 2),
                            "returned": items,
                            "provenance_exact_all": all(i["provenance_exact"] for i in items),
                            "trace_arms": sorted(trace.keys()) if isinstance(trace, dict) else None})

    case_scores = []
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        score = L.score_longitudinal_case(fixture, case, returned)
        record["failure_classes"] = list(score.failure_classes)
        case_scores.append(score)
    lifecycle_scores = [L.score_lifecycle_state(fixture, cid, evidence) for cid, evidence in lifecycle_by_checkpoint.items()]

    payload = {
        "repetition": args.repetition, "bank": args.bank,
        "cases": records, "checkpoint_state": checkpoint_state,
        "lifecycle": {cid: [{"canonical_id": e.canonical_id, "active_current": e.active_current,
                             "historically_recoverable": e.historically_recoverable,
                             "disposition": str(e.disposition)} for e in evidence]
                      for cid, evidence in lifecycle_by_checkpoint.items()},
        "lifecycle_failures": {s.checkpoint_id: list(s.failure_classes) for s in lifecycle_scores},
        "failure_totals": L.aggregate_failure_classes(case_scores),
        "lifecycle_failure_totals": L.aggregate_failure_classes(lifecycle_scores),
        "receipts": [{"canonical_observation_id": v, "document_id": k} for k, v in sorted(native_to_canonical.items())],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    failing = {k: v for k, v in payload["failure_totals"].items() if v}
    print(f"rep{args.repetition}: {len(records)} cases, failures {failing or 'none'}; "
          f"provenance exact {all(r['provenance_exact_all'] for r in records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
