#!/usr/bin/env python3
"""Gen80: two configurations inside one scope, with both axes bound natively.

The Gen79 configuration binding is layered ON TOP of the Gen78 scope binding.
Scope identity, ingest policy and every other adapter behaviour are unchanged -
one variable moves.

Only LQ03 qualifies: same scope (`server:forge`), expecting the C1 observation
and prohibiting the C2 one. Cross-scope cases belong to Gen78 and are not
repeated here.

Clean retrieval is reported explicitly. An engine that returns nothing also
avoids `configuration_collapse`, and that must not be able to pass as isolation.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                          # noqa: E402
from memory_bakeoff.providers import scope_bound as SB                # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB        # noqa: E402

OUT = ROOT / "results" / "configuration_isolation_gen80"
CASE = "LQ03"
LIMIT = 5


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def the_case(fixture):
    return next(c for c in fixture.cases if c.id == CASE)


def prefix_for(fixture):
    return fixture.prefix(the_case(fixture).checkpoint_id)


def score(fixture, records):
    case = the_case(fixture)
    for record in records:
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        classes = list(L.score_longitudinal_case(fixture, case, returned).failure_classes)
        record.update({
            "failure_classes": classes,
            "returned_ids": sorted(set(returned)),
            "configuration_collapse":
                str(L.FailureClass.CONFIGURATION_COLLAPSE) in classes,
            # Explicit, so an empty answer cannot masquerade as isolation.
            "returned_expected": bool(set(case.expected_ids) & set(returned)),
            "returned_prohibited": bool(set(case.prohibited_ids) & set(returned)),
            "clean_retrieval": bool(set(case.expected_ids) & set(returned))
                               and not set(case.prohibited_ids) & set(returned),
        })
    return records


def run_perseus(fixture, repetition, root):
    g29 = load("run_perseus_gen29_longitudinal")
    A = g29.A
    home = root / f"rep{repetition}"
    home.mkdir(parents=True, exist_ok=True)
    db, key = home / "vault.sqlite", home / "vault.key"
    g29.sh([g29.BIN, "keygen", "--key-file", key])
    native = {}
    for observation in prefix_for(fixture):
        body = A.body_for_observation(observation)
        A.assert_public_only(body)
        receipt = json.loads(g29.sh(
            [g29.BIN, "write", "--db", db, "--encryption-key", key,
             "--category", CB.perseus_write(observation.configuration)["category"],
             "--key", A.key_for_observation(observation.id),
             "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
             "--workspace-hash", A.workspace_for_scope(observation.scope)]))
        native[receipt["id"]] = observation.id
        time.sleep(0.05)
    case = the_case(fixture)
    snap_db, snap_key = g29.snapshot(db, key, home / "snap")
    server = g29.Server(snap_db, snap_key)
    try:
        arguments = {"query": case.query, "limit": LIMIT, "mode": "hybrid",
                     "workspace_hash": A.workspace_for_scope(case.scope),
                     **CB.perseus_query(case.configuration)}
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
            items.append({"native_rank": rank,
                          "canonical_id": canonical if exact else None,
                          "provenance_exact": exact})
    finally:
        server.stop()
    return [{"case_id": CASE, "scope": case.scope, "configuration": case.configuration,
             "bound_scope": arguments["workspace_hash"],
             "bound_configuration": arguments["category"], "returned": items}]


def run_mem0(fixture, repetition, root):
    g32 = load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    M = g32.M
    memory = Memory.from_config(g32.config_for(
        str(root / f"rep{repetition}"), f"bakeoff-gen80-r{repetition}"))
    native = {}
    for observation in prefix_for(fixture):
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        result = memory.add(
            payload["text"],
            user_id=SB.mem0_write(observation.scope)["user_id"],
            agent_id=CB.mem0_write(observation.configuration)["agent_id"],
            infer=payload["infer"], metadata=payload["metadata"])
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native[row["id"]] = observation.id
        time.sleep(0.02)
    case = the_case(fixture)
    filters = {**SB.mem0_query(case.scope)["filters"],
               **CB.mem0_query(case.configuration)["filters"]}
    raw = memory.search(case.query, filters=filters, limit=LIMIT,
                        threshold=M.THRESHOLD)
    hits = raw.get("results") if isinstance(raw, dict) else raw
    items = []
    for rank, hit in enumerate((hits or [])[:LIMIT], start=1):
        marker = (hit.get("metadata") or {}).get("record_id")
        canonical = native.get(hit.get("id"))
        exact = canonical is not None and marker == canonical
        items.append({"native_rank": rank,
                      "canonical_id": canonical if exact else None,
                      "provenance_exact": exact})
    return [{"case_id": CASE, "scope": case.scope, "configuration": case.configuration,
             "bound_scope": filters["user_id"],
             "bound_configuration": filters["agent_id"], "returned": items}]


def run_agentmemory(fixture, repetition, root):
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13, A = g33.g13, g33.A
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen80-r{repetition}-",
                                  dir="/private/tmp"))
    run = f"g80r{repetition}"
    case = the_case(fixture)
    agent = SB.agentmemory_write(case.scope, run=run)["agentId"]
    native, launcher = {}, None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state,
                                                     repetition, agent)
        for observation in prefix_for(fixture):
            observation_agent = SB.agentmemory_write(observation.scope, run=run)["agentId"]
            payload = {**A.remember_arguments(observation, observation_agent),
                       "agentId": observation_agent,
                       **CB.agentmemory_write(observation.configuration)}
            A.assert_public_only(payload)
            g13.request_json(base, "/agentmemory/remember", body=payload)
            time.sleep(0.05)
            for row in g33.native_rows(base, observation_agent):
                for source in (row.get("sourceObservationIds") or []):
                    native[row.get("id")] = source
        arguments = {**A.search_arguments(case, agent, LIMIT), "agentId": agent,
                     **CB.agentmemory_query(case.configuration)}
        raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
        items = []
        for rank, hit in enumerate((raw.get("results") or [])[:LIMIT], start=1):
            canonical = (native.get(hit.get("obsId"))
                         or (hit.get("sourceObservationIds") or [None])[0])
            exact = canonical in {o.id for o in fixture.observations}
            items.append({"native_rank": rank,
                          "canonical_id": canonical if exact else None,
                          "provenance_exact": exact})
    finally:
        try:
            g13.stop_service(g33.AGENTMEMORY, state, repetition, agent, launcher)
        except Exception:
            pass
    return [{"case_id": CASE, "scope": case.scope, "configuration": case.configuration,
             "bound_scope": agent,
             "bound_configuration": arguments["project"], "returned": items}]


ENGINES = {"perseus": run_perseus, "mem0": run_mem0, "agentmemory": run_agentmemory}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=sorted(ENGINES))
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()

    fixture = L.build_longitudinal_fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"gen80-{args.engine}-"))
    repetitions = []
    for repetition in range(1, args.repetitions + 1):
        records = score(fixture, ENGINES[args.engine](fixture, repetition, root))
        repetitions.append({"repetition": repetition, "records": records})
        for record in records:
            print(f"{args.engine} rep{repetition}: collapse="
                  f"{record['configuration_collapse']} clean={record['clean_retrieval']} "
                  f"got={record['returned_ids']}", flush=True)

    (OUT / f"{args.engine}.json").write_text(json.dumps({
        "engine": args.engine, "generation": 80,
        "case": CASE,
        "ablation": "Gen79 configuration binding layered on the Gen78 scope binding; "
                    "scope identity, ingest policy and all other adapter behaviour "
                    "unchanged",
        "ingestion": "prefix of the queried checkpoint only",
        "scope_binding": {k: v for k, v in SB.BINDINGS.get(args.engine, {}).items()
                          if k not in ("write", "query")},
        "configuration_binding": {k: v for k, v in CB.BINDINGS[args.engine].items()
                                  if k not in ("write", "query")},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "configuration_collapse_total": sum(
            1 for rep in repetitions for r in rep["records"]
            if r["configuration_collapse"]),
        "clean_retrieval_total": sum(1 for rep in repetitions for r in rep["records"]
                                     if r["clean_retrieval"]),
        "case_runs": sum(len(rep["records"]) for rep in repetitions),
    }, indent=2, sort_keys=True, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
