#!/usr/bin/env python3
"""Gen103: localise exactly when and why agentmemory loses the kestrel current record.

AgentMemory only. Minimal TWO-RECORD probes, no distractors, no broad rerun. Both
v2 and v3 orders as controls. Semantic content is unchanged: the two kestrel
records exactly as the fixture holds them.

At every stage the decisive internal state is recorded rather than inferred:
stored rows with their retirement metadata, and search visibility. The result
must localise to write-time mutation, lifecycle state, or retrieval filtering.
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

OUT = EV.next_attempt(ROOT, 103)
CORE = "oncall:kestrel"
LIMIT = 5


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def snapshot(g13, base, agent, query, project):
    """The decisive state: stored rows with retirement metadata, and search."""
    rows = g13.request_json(base, "/agentmemory/memories", method="GET") \
        if False else None
    try:
        listed = g13.request_json(base, "/agentmemory/smart-search",
                                  body={"agentId": agent, "project": project,
                                        "query": query, "limit": LIMIT})
        hits = [{"obsId": h.get("obsId"), "title": h.get("title"),
                 "score": h.get("score")} for h in (listed.get("results") or [])]
    except Exception as exc:                       # noqa: BLE001
        hits = [{"error": str(exc)[:120]}]
    return {"search_hits": hits}


def stored_rows(g33, base, agent):
    rows = g33.native_rows(base, agent)
    out = []
    for row in rows:
        out.append({k: row.get(k) for k in
                    ("id", "title", "isLatest", "version", "parentId",
                     "supersedes", "sourceObservationIds", "project", "agentId")
                    if k in row})
    return out


def probe(order_name, order, fixture, g13, g33, A, tag, include_foreign=False):
    """`include_foreign` tests the one rule source inspection named: remember.ts
    skips supersession across an explicit project boundary. The foreign record is
    the only fixture record the two-record probe omits, and it is the only
    difference between this probe and the Gen102 run."""
    core_records = {o.role: o for o in fixture.observations
                    if o.core == CORE and o.role in ("current", "superseded",
                                                     "foreign")}
    state = Path(tempfile.mkdtemp(prefix=f"g103-{tag}-", dir="/private/tmp"))
    # Unique per invocation. A fixed run id reuses the agentId, and a second
    # invocation then lists BOTH runs' rows - which showed up as four rows where
    # there should be two. The conclusion was unaffected, but a localisation
    # claim must not rest on a store shared with an earlier probe.
    run = f"g103{tag}{int(time.time())}"
    case = next(c for c in fixture.cases if c.core == CORE and c.load == 0)
    agent = SB.agentmemory_write(case.scope, run=run)["agentId"]
    project = CB.agentmemory_write(case.configuration)["project"]
    stages = []
    launcher = None
    try:
        base, _startup, launcher = g13.start_service(g33.AGENTMEMORY, state, 1, agent)
        stages.append({"stage": "before any write",
                       "rows": stored_rows(g33, base, agent),
                       **snapshot(g13, base, agent, case.query, project)})
        sequence = list(order) + (["foreign"] if include_foreign else [])
        for index, role in enumerate(sequence, start=1):
            observation = core_records[role]
            # The foreign record carries its OWN scope and configuration, exactly
            # as the fixture and the Gen96 bindings put them.
            write_agent = SB.agentmemory_write(observation.scope, run=run)["agentId"]
            write_project = CB.agentmemory_write(observation.configuration)["project"]
            g13.request_json(base, "/agentmemory/remember", body={
                "content": observation.text, "type": "observation",
                "sourceObservationIds": [observation.id],
                "agentId": write_agent, "project": write_project})
            time.sleep(0.2)
            stages.append({
                "stage": f"after write {index}: {role} ({observation.id})",
                "written": observation.id, "role": role,
                "rows": stored_rows(g33, base, agent),
                **snapshot(g13, base, agent, case.query, project)})
    finally:
        if launcher is not None:
            g13.stop_service(g33.AGENTMEMORY, state, 1, agent, launcher)
    return {"order": order_name, "sequence": list(order), "stages": stages}


def main() -> int:
    fixture = V3.build_fixture()
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13, A = g33.g13, g33.A
    probes = {
        "v3_superseded_first": probe("v3 (superseded first, current second)",
                                     ("superseded", "current"), fixture, g13, g33,
                                     A, "v3"),
        "v2_current_first": probe("v2 (current first, superseded second)",
                                  ("current", "superseded"), fixture, g13, g33,
                                  A, "v2"),
        "v3_with_foreign": probe("v3 plus the foreign record (project guard)",
                                 ("superseded", "current"), fixture, g13, g33,
                                 A, "v3f", include_foreign=True),
    }
    payload = {
        "engine": "agentmemory", "core": CORE,
        "probe": "two records only; no distractors; semantic content unchanged",
        "write_time_rule_from_source": {
            "file": "src/functions/remember.ts",
            "rule": "on each write, scan existing candidates; the FIRST with "
                    "jaccard > 0.7 is superseded by the INCOMING record",
            "effect_on_superseded": "isLatest=false; the row STAYS in KV and is "
                                    "REMOVED from both search indexes",
            "project_guard": "never supersedes across an explicit project boundary",
            "note": "a separate maintenance pass, src/functions/auto-forget.ts, "
                    "retires the record with the OLDER createdAt at threshold 0.9; "
                    "it is not the write path",
        },
        "probes": probes,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "localization.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))
    for name, entry in probes.items():
        print(f"=== {entry['order']}")
        for stage in entry["stages"]:
            titles = [h.get("title", "")[:28] for h in stage["search_hits"]]
            flags = [(r.get("title", "")[:20], r.get("isLatest"),
                      r.get("supersedes")) for r in stage["rows"]]
            print(f"  {stage['stage']}")
            print(f"    rows   : {flags}")
            print(f"    search : {titles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
