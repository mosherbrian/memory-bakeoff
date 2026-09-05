#!/usr/bin/env python3
"""Gen97: the first real interference run, on frozen `interference-v1`.

One engine per invocation, four load levels, three repetitions. Each engine keeps
its own retrieval budget and strategy (Gen96): a native result count for perseus,
mem0 and agentmemory; `max_tokens` for hindsight, whose forgetting/displacement
attribution is therefore recorded NOT_DEMONSTRABLE rather than inferred.

No tuning after exposure. No cross-engine pooled comparison - the summary is a
within-engine curve, and `assert_within_engine_only` guards it.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF                        # noqa: E402
from memory_bakeoff import round3_adapters as R3                      # noqa: E402
from memory_bakeoff.providers import scope_bound as SB                # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB        # noqa: E402

OUT = ROOT / "results" / "interference_gen97"
LIMIT = 5                 # the harness window for engines that express one
HINDSIGHT_MAX_TOKENS = 4096
REPETITIONS = (1, 2, 3)
FORBIDDEN = ("role", "core", "expected", "prohibited_stale", "prohibited_foreign")


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def public_body(observation) -> dict[str, str]:
    """Publication-safe fields only. Role and core are fixture truth and stay out."""
    body = {"assertion": observation.text, "canonical_observation_id": observation.id,
            "scope": observation.scope, "configuration": observation.configuration,
            "source_kind": "interference_observation"}
    leaked = sorted(set(body) & set(FORBIDDEN))
    if leaked:
        raise ValueError(f"write envelope leaks fixture truth: {leaked}")
    return body


# Which records a case ingests. v2 overrides this with its core-aware resolver;
# a global rather than an argument so the four engine functions stay unchanged.
VISIBLE_IDS = ITF.visible_ids


def observations_for(fixture, case):
    """Records to ingest, IN THE RESOLVER'S ORDER.

    The first version took `set(VISIBLE_IDS(...))` and then iterated
    `fixture.observations`, which discarded the resolver's sequence and wrote
    records in fixture-construction order. Swapping in v3's core-aware,
    chronology-correct resolver therefore changed WHICH records were ingested
    and never the ORDER they were written in - so Gen102 ran the v2 order while
    reporting itself as v3 (found by the Gen104 trace).
    """
    return ITF.ordered_observations(fixture, case, VISIBLE_IDS)


def ingest(fixture, case):
    """Yield the records to write, and check on the way out that the caller
    consumed them in the resolver's order.

    Gen104's invariant, applied where it can actually fire: `observations_for`
    returns the right order by construction, so the residual risk is an engine
    function reordering after the call. This checks what was CONSUMED.
    """
    resolved = [o.id for o in observations_for(fixture, case)]
    consumed = []
    for observation in ingest(fixture, case):
        consumed.append(observation.id)
        yield observation
    ITF.assert_ingest_order_preserved(resolved, consumed)


# --- perseus --------------------------------------------------------------
def run_perseus(fixture, case, repetition, root):
    g29 = load("run_perseus_gen29_longitudinal")
    home = root / f"{case.id}-rep{repetition}"
    home.mkdir(parents=True, exist_ok=True)
    db, key = home / "vault.sqlite", home / "vault.key"
    g29.sh([g29.BIN, "keygen", "--key-file", key])
    native = {}
    for observation in ingest(fixture, case):
        body = public_body(observation)
        receipt = json.loads(g29.sh(
            [g29.BIN, "write", "--db", db, "--encryption-key", key,
             "--category", CB.perseus_write(observation.configuration)["category"],
             "--key", f"record-{observation.id}",
             "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
             "--workspace-hash", SB.scope_token(observation.scope)]))
        native[receipt["id"]] = observation.id
    snap_db, snap_key = g29.snapshot(db, key, home / "snap")
    server = g29.Server(snap_db, snap_key)
    try:
        arguments = {"query": case.query, "limit": LIMIT, "mode": "hybrid",
                     "workspace_hash": SB.scope_token(case.scope),
                     **CB.perseus_query(case.configuration)}
        payload = server.recall(arguments)
        hits = [hit.get("id") for hit in payload.get("items", [])[:LIMIT]]
        ITF.assert_hits_map_to_live_identity(hits, list(native), native)
        return [native.get(h) for h in hits], arguments
    finally:
        server.stop()


# --- mem0 -----------------------------------------------------------------
def run_mem0(fixture, case, repetition, root):
    g32 = load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    memory = Memory.from_config(g32.config_for(
        str(root / f"{case.id}-rep{repetition}"),
        f"bakeoff-{case.id.lower()}-r{repetition}"))
    native = {}
    for observation in ingest(fixture, case):
        body = public_body(observation)
        result = memory.add(
            observation.text,
            user_id=SB.mem0_write(observation.scope)["user_id"],
            agent_id=CB.mem0_write(observation.configuration)["agent_id"],
            infer=False, metadata={"record_id": observation.id, **body})
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native[row["id"]] = observation.id
    filters = R3.merge_payloads(SB.mem0_query(case.scope),
                               CB.mem0_query(case.configuration))["filters"]
    raw = memory.search(case.query, filters=filters, limit=LIMIT,
                        threshold=g32.M.THRESHOLD)
    hits = raw.get("results") if isinstance(raw, dict) else raw
    returned = []
    for hit in (hits or [])[:LIMIT]:
        marker = (hit.get("metadata") or {}).get("record_id")
        canonical = native.get(hit.get("id"))
        returned.append(canonical if canonical is not None and marker == canonical else None)
    return returned, {"filters": filters, "limit": LIMIT}


# --- agentmemory ----------------------------------------------------------
def run_agentmemory(fixture, case, repetition, root):
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13 = g33.g13
    state = Path(tempfile.mkdtemp(prefix=f"am-{case.id.lower()}-r{repetition}-",
                                  dir="/private/tmp"))
    run = f"g{case.id.replace(chr(45), chr(48)).lower()}r{repetition}"
    agent = SB.agentmemory_write(case.scope, run=run)["agentId"]
    native, launcher = {}, None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state,
                                                     repetition, agent)
        for observation in ingest(fixture, case):
            observation_agent = SB.agentmemory_write(observation.scope, run=run)["agentId"]
            payload = {"content": observation.text, "type": "observation",
                       "sourceObservationIds": [observation.id],
                       "agentId": observation_agent,
                       **CB.agentmemory_write(observation.configuration)}
            g13.request_json(base, "/agentmemory/remember", body=payload)
            for row in g33.native_rows(base, observation_agent):
                for source in (row.get("sourceObservationIds") or []):
                    native[row.get("id")] = source
        arguments = {"agentId": agent, "query": case.query, "limit": LIMIT,
                     **CB.agentmemory_query(case.configuration)}
        raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
        hits = [h.get("obsId") for h in (raw.get("results") or [])[:LIMIT]]
        live = [r.get("id") for r in g33.native_rows(base, agent)
                if r.get("isLatest") is not False]
        ITF.assert_hits_map_to_live_identity(hits, live, native)
        returned = [native.get(h) for h in hits]
        return returned, arguments
    finally:
        g13.stop_service(g33.AGENTMEMORY, state, repetition, agent, launcher)


# --- hindsight ------------------------------------------------------------
def run_hindsight(fixture, case, repetition, root):
    from hindsight_client import Hindsight
    client = Hindsight()
    bank = f"bakeoff-{case.id.lower()}-r{repetition}"
    native = {}
    for observation in ingest(fixture, case):
        body = public_body(observation)
        result = client.retain(
            bank_id=bank, content=observation.text,
            metadata={"record_id": observation.id, **body},
            tags=CB.hindsight_write(observation.configuration)["tags"])
        document_id = getattr(result, "document_id", None) or f"record-{observation.id}"
        native[document_id] = observation.id
    arguments = {"bank_id": bank, "query": case.query,
                 "max_tokens": HINDSIGHT_MAX_TOKENS,
                 **CB.hindsight_query(case.configuration)}
    raw = client.recall(**arguments)
    got = getattr(raw, "results", None) or (raw.get("results") if isinstance(raw, dict) else [])
    returned, hits = [], []
    for hit in (got or []):
        get = (lambda k: hit.get(k)) if isinstance(hit, dict) else (lambda k: getattr(hit, k, None))
        metadata = get("metadata") or {}
        marker = metadata.get("record_id") if isinstance(metadata, dict) else None
        hits.append(get("document_id"))
        canonical = native.get(get("document_id"))
        returned.append(canonical if canonical is not None and marker == canonical else None)
    ITF.assert_hits_map_to_live_identity(hits, list(native), native)
    return returned, arguments


ENGINES = {"perseus": run_perseus, "mem0": run_mem0,
           "agentmemory": run_agentmemory, "hindsight": run_hindsight}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=sorted(ENGINES))
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    engine = args.engine
    expressible = R3.BUDGET_SURFACE[engine]["window_expressible"]
    fixture = ITF.build_fixture()
    root = Path(args.root or tempfile.mkdtemp(prefix=f"gen97-{engine}-",
                                              dir="/private/tmp"))
    rows = []
    for case in fixture.cases:
        for repetition in REPETITIONS:
            started = time.perf_counter()
            returned, arguments = ENGINES[engine](fixture, case, repetition, root)
            latency = (time.perf_counter() - started) * 1000
            ids = [i for i in returned if i]
            scored = ITF.score_case(fixture, case, ids, LIMIT,
                                    window_expressible=expressible)
            rows.append({"engine": engine, "load": case.load, "case": case.id,
                         "repetition": repetition,
                         "requested": ("limit=%d" % LIMIT) if expressible
                                      else f"max_tokens={HINDSIGHT_MAX_TOKENS}",
                         "raw_returned": returned, "unmapped": returned.count(None),
                         "latency_ms": round(latency, 1),
                         "arguments": {k: v for k, v in arguments.items()
                                       if k != "query"},
                         **scored})
            print(f"  L{case.load:<3} rep{repetition}  {scored['mechanisms']}")

    payload = {"engine": engine, "fixture_version": ITF.FIXTURE_VERSION,
               "scorer_version": ITF.SCORER_VERSION,
               "budget": R3.BUDGET_SURFACE[engine],
               "saturation": R3.saturation_meaning(engine),
               "rows": rows}
    R3.assert_within_engine_only(payload)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{engine}.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(f"\nwrote {OUT / (engine + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
