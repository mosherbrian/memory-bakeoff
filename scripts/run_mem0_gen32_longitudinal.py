#!/usr/bin/env python3
"""Gen32: Mem0 2.0.19 raw infer=False against the frozen longitudinal-v1 ruler."""
from __future__ import annotations

import argparse, hashlib, json, sqlite3, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
UPSTREAM = ROOT / "external/mem0"
if str(UPSTREAM) not in sys.path:
    sys.path.insert(0, str(UPSTREAM))

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import mem0_longitudinal as M

LIMIT = 5
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"


def config_for(path: str, collection: str) -> dict:
    return {
        "llm": {"provider": "openai", "config": {"api_key": "not-used-in-raw-mode"}},
        "embedder": {"provider": "fastembed", "config": {"model": "thenlper/gte-large",
                                                          "embedding_dims": M.EMBEDDING_DIMS}},
        "vector_store": {"provider": "qdrant", "config": {"path": path, "collection_name": collection,
                                                           "embedding_model_dims": M.EMBEDDING_DIMS, "on_disk": True}},
        "history_db_path": str(Path(path) / "history.db"),
    }


def history_counts(path: str) -> dict:
    db = Path(path) / "history.db"
    if not db.exists():
        return {}
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in tables}
    finally:
        con.close()


def run_repetition(fixture, repetition: int, root: Path) -> dict:
    from mem0 import Memory

    path = str(root / f"rep{repetition}")
    collection = f"memory-bakeoff-gen32-r{repetition}"
    memory = Memory.from_config(config_for(path, collection))

    checkpoints = {c.ingestion_order: c for c in fixture.checkpoints}
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    native_to_canonical: dict[str, str] = {}
    records, checkpoint_state, lifecycle_by_checkpoint = [], {}, {}

    for observation in fixture.observations:
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        result = memory.add(payload["text"], user_id=payload["user_id"], infer=payload["infer"],
                            metadata=payload["metadata"])
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native_to_canonical[row["id"]] = observation.id
        time.sleep(0.02)

        checkpoint = checkpoints.get(observation.ingestion_order)
        if checkpoint is None:
            continue

        stored = memory.get_all(filters={"user_id": M.USER_ID})
        stored_rows = stored.get("results") if isinstance(stored, dict) else stored
        by_canonical = {}
        for row in (stored_rows or []):
            marker = (row.get("metadata") or {}).get("record_id")
            if marker:
                by_canonical[marker] = row.get("id")
                native_to_canonical.setdefault(row.get("id"), marker)
        prefix_ids = {o.id for o in fixture.prefix(checkpoint.id)}
        checkpoint_state[checkpoint.id] = {"points": len(stored_rows or []),
                                           "expected_prefix": len(prefix_ids),
                                           "history": history_counts(path)}
        lifecycle_by_checkpoint[checkpoint.id] = [
            L.LifecycleEvidence(cid, active_current=cid in by_canonical,
                                historically_recoverable=True if cid in by_canonical else None,
                                disposition=L.LifecycleDisposition.ACTIVE_CURRENT if cid in by_canonical else L.LifecycleDisposition.UNKNOWN,
                                evidence_strength="native_point_row",
                                native_evidence=f"qdrant point present={cid in by_canonical}")
            for cid in sorted(prefix_ids)]

        prefix_sha = hashlib.sha256(L.canonical_json([o.public_dict() for o in fixture.prefix(checkpoint.id)]).encode()).hexdigest()
        for case in cases_by_checkpoint.get(checkpoint.id, []):
            arguments = M.search_arguments(case, LIMIT)
            started = time.perf_counter()
            raw = memory.search(arguments["query"], filters=arguments["filters"],
                                limit=arguments["limit"], threshold=arguments["threshold"])
            latency_ms = (time.perf_counter() - started) * 1000
            hits = raw.get("results") if isinstance(raw, dict) else raw
            items = []
            for rank, hit in enumerate((hits or [])[:LIMIT], start=1):
                metadata = hit.get("metadata") or {}
                marker = metadata.get("record_id")
                native_id = hit.get("id")
                canonical = native_to_canonical.get(native_id)
                exact = canonical is not None and marker == canonical
                items.append({"native_rank": rank, "native_id": native_id, "record_id": marker,
                              "source_ref": metadata.get("source_ref"),
                              "canonical_id": canonical if exact else None, "provenance_exact": exact,
                              "score": hit.get("score"), "text": (hit.get("memory") or hit.get("text") or "")[:110]})
            records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                            "ingested_prefix_sha256": prefix_sha,
                            "native_temporal_operation": M.native_operation(case),
                            "requested_limit": LIMIT, "threshold": M.THRESHOLD,
                            "latency_ms": round(latency_ms, 2), "returned": items,
                            "provenance_exact_all": all(i["provenance_exact"] for i in items)})

    case_scores = []
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        score = L.score_longitudinal_case(fixture, case, returned)
        record["failure_classes"] = list(score.failure_classes)
        case_scores.append(score)
    lifecycle_scores = [L.score_lifecycle_state(fixture, cid, ev) for cid, ev in lifecycle_by_checkpoint.items()]

    return {"repetition": repetition, "collection": collection, "cases": records,
            "checkpoint_state": checkpoint_state,
            "lifecycle": {cid: [{"canonical_id": e.canonical_id, "active_current": e.active_current,
                                 "historically_recoverable": e.historically_recoverable,
                                 "disposition": str(e.disposition)} for e in ev]
                          for cid, ev in lifecycle_by_checkpoint.items()},
            "lifecycle_failures": {s.checkpoint_id: list(s.failure_classes) for s in lifecycle_scores},
            "failure_totals": L.aggregate_failure_classes(case_scores),
            "lifecycle_failure_totals": L.aggregate_failure_classes(lifecycle_scores),
            "receipts": [{"native_id": k, "canonical_observation_id": v} for k, v in sorted(native_to_canonical.items())]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--out", default=str(ROOT / "results/mem0_gen32_longitudinal"))
    args = parser.parse_args()

    if L.fixture_sha256() != FIXTURE_SHA or L.scorer_contract_sha256() != SCORER_SHA:
        raise SystemExit("frozen ruler hash drift; refusing to run")
    fixture = L.build_longitudinal_fixture()
    temp = tempfile.TemporaryDirectory(prefix="memory-bakeoff-gen32-", dir="/private/tmp")
    reps = [run_repetition(fixture, n, Path(temp.name)) for n in range(1, args.repetitions + 1)]
    if L.fixture_sha256() != FIXTURE_SHA:
        raise SystemExit("fixture hash drifted during the run")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for rep in reps:
        (out / f"repetition-{rep['repetition']}.json").write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    for rep in reps:
        failing = {k: v for k, v in rep["failure_totals"].items() if v}
        print(f"  rep{rep['repetition']}: {len(rep['cases'])} cases, failures {failing or 'none'}; "
              f"provenance exact {all(c['provenance_exact_all'] for c in rep['cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
