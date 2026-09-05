#!/usr/bin/env python3
"""Gen70 hindsight repetition: over-ingest the timeline, then ask as-of questions.

Mirrors gen31_repetition.py exactly except for the ingestion plan: every
observation is retained before any question is asked, so the store holds facts
the questioner should not yet know.
"""
from __future__ import annotations

import argparse, hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                     # noqa: E402
from memory_bakeoff import temporal_reachability as T            # noqa: E402
from memory_bakeoff.providers import hindsight_longitudinal as H # noqa: E402

LIMIT = 5
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"


def result_rows(raw, native_to_canonical):
    from gen31_repetition import result_rows as rows
    return rows(raw, native_to_canonical)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--bank", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from hindsight_client import Hindsight

    if L.fixture_sha256() != FIXTURE_SHA:
        raise SystemExit("longitudinal-v1 fixture hash drift; refusing to run")

    fixture = L.build_longitudinal_fixture()
    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    native_to_canonical: dict[str, str] = {}
    for observation in fixture.observations:
        payload = H.retain_arguments(observation, args.bank)
        H.assert_public_only(payload)
        client.retain(**payload)
        native_to_canonical[payload["document_id"]] = observation.id
        time.sleep(0.05)

    probe = T.LEAKAGE_PROBE
    have = {c.checkpoint_id for c in fixture.cases}
    records = []
    for checkpoint_id in [cp for cp in probe["query_as_of_checkpoints"] if cp in have]:
        prefix_sha = hashlib.sha256(L.canonical_json(
            [o.public_dict() for o in fixture.prefix(checkpoint_id)]).encode()).hexdigest()
        for case in cases_by_checkpoint.get(checkpoint_id, []):
            arguments = H.recall_arguments(case, args.bank, LIMIT)
            started = time.perf_counter()
            raw = client.recall(**arguments)
            latency_ms = (time.perf_counter() - started) * 1000
            records.append({
                "case_id": case.id, "checkpoint_id": checkpoint_id,
                "queried_as_of": checkpoint_id,
                "ingested_through": probe["ingest_through_checkpoint"],
                "ingested_prefix_sha256": prefix_sha,
                "native_temporal_operation": H.native_operation(case),
                "query_timestamp": arguments.get("query_timestamp"),
                "requested_limit": LIMIT, "latency_ms": round(latency_ms, 2),
                "returned": result_rows(raw, native_to_canonical),
                "reader_answer": None,
            })
            records[-1]["provenance_exact_all"] = all(
                i["provenance_exact"] for i in records[-1]["returned"])

    Path(args.out).write_text(json.dumps(
        {"repetition": args.repetition, "records": records,
         "observations_ingested": len(fixture.observations)},
        indent=2, sort_keys=True, default=str) + "\n")
    print(f"hindsight rep{args.repetition}: {len(records)} probe cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
