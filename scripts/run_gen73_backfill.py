#!/usr/bin/env python3
"""Gen73: the four eligible engines against `backfill-v1`.

Normal ingestion, not Gen70's over-ingestion. The late arrivals here are
intrinsic to the fixture - each is ingested in order but carries an event time
behind facts already stored - so the ordinary prefix plan is the right one and
the engines keep their existing Round-2 configurations.
"""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, sys, tempfile, time
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                       # noqa: E402
from memory_bakeoff import backfill as B                           # noqa: E402

OUT = ROOT / "results" / "backfill_gen73"
LIMIT = 5


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def plan(fixture):
    checkpoints = {c.ingestion_order: c for c in fixture.checkpoints}
    by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        by_checkpoint.setdefault(case.checkpoint_id, []).append(case)
    return checkpoints, by_checkpoint


def prefix_sha(fixture, checkpoint_id: str) -> str:
    return hashlib.sha256(L.canonical_json(
        [o.public_dict() for o in fixture.prefix(checkpoint_id)]).encode()).hexdigest()


def score_all(fixture, records):
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        record["failure_classes"] = list(
            L.score_longitudinal_case(fixture, case, returned).failure_classes)
        record["returned_ids"] = sorted(set(returned))
    return records


def run_mem0(fixture, repetition, root):
    g32 = load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    M = g32.M
    path = str(root / f"rep{repetition}")
    memory = Memory.from_config(g32.config_for(path, f"bakeoff-gen73-r{repetition}"))
    checkpoints, by_checkpoint = plan(fixture)
    native, records = {}, []
    for observation in fixture.observations:
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        result = memory.add(payload["text"], user_id=payload["user_id"],
                            infer=payload["infer"], metadata=payload["metadata"])
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native[row["id"]] = observation.id
        time.sleep(0.02)
        checkpoint = checkpoints.get(observation.ingestion_order)
        if checkpoint is None:
            continue
        stored = memory.get_all(filters={"user_id": M.USER_ID})
        for row in (stored.get("results") if isinstance(stored, dict) else stored) or []:
            marker = (row.get("metadata") or {}).get("record_id")
            if marker:
                native.setdefault(row.get("id"), marker)
        for case in by_checkpoint.get(checkpoint.id, []):
            arguments = M.search_arguments(case, LIMIT)
            raw = memory.search(arguments["query"], filters=arguments["filters"],
                                limit=arguments["limit"], threshold=arguments["threshold"])
            hits = raw.get("results") if isinstance(raw, dict) else raw
            items = []
            for rank, hit in enumerate((hits or [])[:LIMIT], start=1):
                marker = (hit.get("metadata") or {}).get("record_id")
                canonical = native.get(hit.get("id"))
                exact = canonical is not None and marker == canonical
                items.append({"native_rank": rank, "native_id": hit.get("id"),
                              "canonical_id": canonical if exact else None,
                              "provenance_exact": exact})
            records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                            "ingested_prefix_sha256": prefix_sha(fixture, checkpoint.id),
                            "native_temporal_operation": M.native_operation(case),
                            "returned": items})
    return records


def run_perseus(fixture, repetition, root):
    g29 = load("run_perseus_gen29_longitudinal")
    A = g29.A
    home = root / f"rep{repetition}"
    home.mkdir(parents=True, exist_ok=True)
    db, key = home / "vault.sqlite", home / "vault.key"
    g29.sh([g29.BIN, "keygen", "--key-file", key])
    checkpoints, by_checkpoint = plan(fixture)
    native, instants, isos, records = {}, [], [], []
    for observation in fixture.observations:
        body = A.body_for_observation(observation)
        A.assert_public_only(body)
        receipt = json.loads(g29.sh(
            [g29.BIN, "write", "--db", db, "--encryption-key", key,
             "--category", A.CATEGORY, "--key", A.key_for_observation(observation.id),
             "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
             "--workspace-hash", A.workspace_for_scope(observation.scope)]))
        native[receipt["id"]] = observation.id
        instants.append(int({r["id"]: r for r in g29.rows_of(db)}[receipt["id"]]["created_at_unix_ms"]))
        isos.append(observation.ingestion_time.isoformat())
        time.sleep(0.05)
        checkpoint = checkpoints.get(observation.ingestion_order)
        if checkpoint is None:
            continue
        time_base = A.TimeBase(tuple(isos), tuple(instants))
        snap_db, snap_key = g29.snapshot(db, key, home / f"snap-{checkpoint.id}")
        server = g29.Server(snap_db, snap_key)
        try:
            for case in by_checkpoint.get(checkpoint.id, []):
                arguments = A.recall_arguments(case, time_base, LIMIT)
                payload = server.recall(arguments)
                items = []
                for rank, hit in enumerate(payload.get("items", [])[:LIMIT], start=1):
                    canonical = native.get(hit.get("id"))
                    try:
                        body_id = json.loads(hit.get("body_json", "{}")).get(
                            "canonical_observation_id")
                    except json.JSONDecodeError:
                        body_id = None
                    exact = canonical is not None and body_id == canonical
                    items.append({"native_rank": rank, "native_id": hit.get("id"),
                                  "canonical_id": canonical if exact else None,
                                  "provenance_exact": exact})
                records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                                "ingested_prefix_sha256": prefix_sha(fixture, checkpoint.id),
                                "native_temporal_operation": A.native_operation(case),
                                "returned": items})
        finally:
            server.stop()
    return records


def run_agentmemory(fixture, repetition, root):
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13, A = g33.g13, g33.A
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen73-r{repetition}-",
                                  dir="/private/tmp"))
    agent = f"bakeoff-gen73-r{repetition}"
    checkpoints, by_checkpoint = plan(fixture)
    native, records, launcher = {}, [], None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state,
                                                     repetition, agent)
        for observation in fixture.observations:
            payload = A.remember_arguments(observation, agent)
            A.assert_public_only(payload)
            g13.request_json(base, "/agentmemory/remember", body=payload)
            time.sleep(0.05)
            for row in g33.native_rows(base, agent):
                for source in (row.get("sourceObservationIds") or []):
                    native[row.get("id")] = source
            checkpoint = checkpoints.get(observation.ingestion_order)
            if checkpoint is None:
                continue
            for case in by_checkpoint.get(checkpoint.id, []):
                arguments = A.search_arguments(case, agent, LIMIT)
                raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
                items = []
                for rank, hit in enumerate((raw.get("results") or [])[:LIMIT], start=1):
                    canonical = (native.get(hit.get("obsId"))
                                 or (hit.get("sourceObservationIds") or [None])[0])
                    exact = canonical in {o.id for o in fixture.observations}
                    items.append({"native_rank": rank, "obsId": hit.get("obsId"),
                                  "canonical_id": canonical if exact else None,
                                  "provenance_exact": exact})
                records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                                "ingested_prefix_sha256": prefix_sha(fixture, checkpoint.id),
                                "native_temporal_operation": A.native_operation(case),
                                "returned": items})
    finally:
        try:
            g13.stop_service(g33.AGENTMEMORY, state, repetition, agent, launcher)
        except Exception:
            pass
    return records


ENGINES = {"mem0": run_mem0, "perseus": run_perseus, "agentmemory": run_agentmemory}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=sorted(ENGINES))
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()

    fixture = B.build_backfill_fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"gen73-{args.engine}-"))
    repetitions = []
    for repetition in range(1, args.repetitions + 1):
        records = score_all(fixture, ENGINES[args.engine](fixture, repetition, root))
        repetitions.append({"repetition": repetition, "records": records})
        clean = sum(1 for r in records if not r["failure_classes"])
        print(f"{args.engine} rep{repetition}: {clean}/{len(records)} clean", flush=True)

    (OUT / f"{args.engine}.json").write_text(json.dumps({
        "engine": args.engine, "generation": 73,
        "fixture_version": B.FIXTURE_VERSION,
        "fixture_sha256": B.backfill_sha256(fixture),
        "backfill_depth": B.BACKFILL_DEPTH, "backfill_fate": B.BACKFILL_FATE,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
    }, indent=2, sort_keys=True, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
