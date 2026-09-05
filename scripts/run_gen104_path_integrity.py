#!/usr/bin/env python3
"""Gen104: trace identity end-to-end through the EXACT Gen102 agentmemory path.

AgentMemory only. No broad rerun, no scorer change. The kestrel core on
`interference-v3`, reproduced through the same runner code, with identity
recorded at every step:

  write-return -> KV live/retired rows -> accumulated native map ->
  raw search obsIds -> final canonical ids

Gen103 showed the product keeps the right record. Gen102 reported otherwise
through this path. The break is somewhere between those two, and this locates it
rather than naming a suspect.
"""
from __future__ import annotations

import importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV  # noqa: E402
from memory_bakeoff import interference_v3 as V3                  # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB    # noqa: E402
from memory_bakeoff.providers import scope_bound as SB            # noqa: E402

OUT = EV.next_attempt(ROOT, 104)
CORE = "oncall:kestrel"
LIMIT = 5


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def trace_case(fixture, case, repetition):
    """The Gen102 path, step for step, with identity recorded at each one."""
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13 = g33.g13
    state = Path(tempfile.mkdtemp(prefix=f"g104-{case.id.lower()}-", dir="/private/tmp"))
    run = f"g104{case.id.replace('-', '0').lower()}r{repetition}{int(time.time())}"
    agent = SB.agentmemory_write(case.scope, run=run)["agentId"]
    native, steps, launcher = {}, [], None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state,
                                                     repetition, agent)
        by_id = {o.id: o for o in fixture.observations}
        for observation in [by_id[i] for i in V3.visible_ids(fixture, case)]:
            observation_agent = SB.agentmemory_write(observation.scope, run=run)["agentId"]
            payload = {"content": observation.text, "type": "observation",
                       "sourceObservationIds": [observation.id],
                       "agentId": observation_agent,
                       **CB.agentmemory_write(observation.configuration)}
            written = g13.request_json(base, "/agentmemory/remember", body=payload)
            rows = g33.native_rows(base, observation_agent)
            for row in rows:
                for source in (row.get("sourceObservationIds") or []):
                    native[row.get("id")] = source
            steps.append({
                "wrote": observation.id, "role": observation.role,
                "write_agent": observation_agent,
                "write_return": {k: written.get(k) for k in
                                 ("id", "memoryId", "superseded", "supersededId")
                                 if k in (written or {})},
                "rows_listed_for_write_agent": [
                    {"id": r.get("id"), "isLatest": r.get("isLatest"),
                     "src": r.get("sourceObservationIds")} for r in rows],
                "native_map_after": dict(native),
            })
        arguments = {"agentId": agent, "query": case.query, "limit": LIMIT,
                     **CB.agentmemory_query(case.configuration)}
        raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
        hits = (raw.get("results") or [])[:LIMIT]
        # The listing the QUERY agent sees, which is what search draws from.
        query_rows = g33.native_rows(base, agent)
        resolved = [{"obsId": h.get("obsId"),
                     "in_native_map": h.get("obsId") in native,
                     "canonical": native.get(h.get("obsId"))} for h in hits]
    finally:
        if launcher is not None:
            g13.stop_service(g33.AGENTMEMORY, state, repetition, agent, launcher)
    return {
        "case": case.id, "load": case.load, "query_agent": agent,
        "steps": steps,
        "rows_listed_for_query_agent": [
            {"id": r.get("id"), "isLatest": r.get("isLatest"),
             "src": r.get("sourceObservationIds")} for r in query_rows],
        "raw_search_hits": [h.get("obsId") for h in hits],
        "resolved": resolved,
        "final_canonical": [r["canonical"] for r in resolved],
    }


def main() -> int:
    fixture = V3.build_fixture()
    traces = {}
    for load_level in (0, 4):
        case = next(c for c in fixture.cases
                    if c.core == CORE and c.load == load_level)
        traces[f"L{load_level}"] = trace_case(fixture, case, 1)

    payload = {"engine": "agentmemory", "core": CORE,
               "fixture": V3.FIXTURE_VERSION,
               "path": "the exact Gen102 runner code, instrumented",
               "traces": traces}
    # The invariant Gen104 exists to state: every raw search hit must resolve to
    # a live stored identity. A hit that resolves to nothing is a mapping break.
    breaks = {}
    for name, trace in traces.items():
        live_ids = {r["id"] for r in trace["rows_listed_for_query_agent"]
                    if r["isLatest"] is not False}
        breaks[name] = {
            "hits": trace["raw_search_hits"],
            "unmapped_hits": [r["obsId"] for r in trace["resolved"]
                              if not r["in_native_map"]],
            "hits_not_live_for_query_agent": [h for h in trace["raw_search_hits"]
                                              if h not in live_ids],
            "final_canonical": trace["final_canonical"],
        }
    payload["invariant_raw_hits_map_to_a_live_stored_identity"] = breaks
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "trace.json").write_text(json.dumps(payload, indent=1, sort_keys=True,
                                               default=str))
    for name, trace in traces.items():
        print(f"=== {name} ({trace['case']})")
        for step in trace["steps"]:
            print(f"  wrote {step['wrote']:<8} rows={[(r['src'], r['isLatest']) for r in step['rows_listed_for_write_agent']]}")
        print(f"  query-agent rows: {[(r['src'], r['isLatest']) for r in trace['rows_listed_for_query_agent']]}")
        print(f"  raw hits        : {trace['raw_search_hits']}")
        print(f"  resolved        : {trace['final_canonical']}")
        print(f"  unmapped        : {breaks[name]['unmapped_hits']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
