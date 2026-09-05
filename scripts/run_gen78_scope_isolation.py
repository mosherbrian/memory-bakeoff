#!/usr/bin/env python3
"""Gen78: give each engine its own scope primitive, and see if isolation appears.

A configuration ablation, not a product ranking. One variable moves: the frozen
Gen77 binding replaces the constant namespace the Round-2 adapter used. Perseus
is NOT rerun - its scope-bound cases were already measured in Gen68.

Only genuinely cross-scope cases are included. Of the three `scope_truth` cases,
LQ08 and LQ09 pit one scope against another; LQ03 is same-scope with a different
configuration - a configuration question wearing a scope label. Including it
would move the second variable Gen77 deliberately did not freeze.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                        # noqa: E402
from memory_bakeoff.providers import scope_bound as SB              # noqa: E402

OUT = ROOT / "results" / "scope_isolation_gen78"
CROSS_SCOPE_CASES = ("LQ08", "LQ09")
LIMIT = 5


def load(script: str):
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def cases_for(fixture):
    return [c for c in fixture.cases if c.id in CROSS_SCOPE_CASES]


def ingestion_prefix(fixture):
    """Only what the queried checkpoint may know.

    Both cross-scope cases sit at the same checkpoint. Ingesting the whole
    timeline would import Gen70's over-ingestion and charge future_leakage as an
    artefact of this runner rather than a property of the binding.
    """
    checkpoints = {c.checkpoint_id for c in cases_for(fixture)}
    if len(checkpoints) != 1:
        raise SystemExit(f"cross-scope cases span checkpoints {sorted(checkpoints)}; "
                         "the prefix rule needs revisiting")
    return fixture.prefix(next(iter(checkpoints)))


def score(fixture, records):
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        classes = list(L.score_longitudinal_case(fixture, case, returned).failure_classes)
        record["failure_classes"] = classes
        record["returned_ids"] = sorted(set(returned))
        record["scope_collapse"] = str(L.FailureClass.SCOPE_COLLAPSE) in classes
    return records


def run_mem0(fixture, repetition, root):
    g32 = load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    M = g32.M
    memory = Memory.from_config(g32.config_for(
        str(root / f"rep{repetition}"), f"bakeoff-gen78-r{repetition}"))
    native = {}
    for observation in ingestion_prefix(fixture):
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        bound = SB.mem0_write(observation.scope)          # scope, not a constant
        result = memory.add(payload["text"], user_id=bound["user_id"],
                            infer=payload["infer"], metadata=payload["metadata"])
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native[row["id"]] = observation.id
        time.sleep(0.02)
    records = []
    for case in cases_for(fixture):
        arguments = M.search_arguments(case, LIMIT)
        bound = SB.mem0_query(case.scope)
        raw = memory.search(arguments["query"], filters=bound["filters"],
                            limit=LIMIT, threshold=arguments["threshold"])
        hits = raw.get("results") if isinstance(raw, dict) else raw
        items = []
        for rank, hit in enumerate((hits or [])[:LIMIT], start=1):
            marker = (hit.get("metadata") or {}).get("record_id")
            canonical = native.get(hit.get("id"))
            exact = canonical is not None and marker == canonical
            items.append({"native_rank": rank, "canonical_id": canonical if exact else None,
                          "provenance_exact": exact})
        records.append({"case_id": case.id, "scope": case.scope,
                        "bound_identity": bound["filters"]["user_id"],
                        "returned": items})
    return records


def run_agentmemory(fixture, repetition, root):
    g33 = load("run_agentmemory_gen33_longitudinal.py")
    g13, A = g33.g13, g33.A
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen78-r{repetition}-",
                                  dir="/private/tmp"))
    run = f"g78r{repetition}"
    scopes = sorted({o.scope for o in fixture.observations})
    native, records, launchers = {}, [], {}
    try:
        # One service instance; a distinct agentId per scope is the binding.
        base, _startup, launcher = g13.start_service(
            g33.AGENTMEMORY, state, repetition,
            SB.agentmemory_write(scopes[0], run=run)["agentId"])
        launchers["main"] = launcher
        for observation in ingestion_prefix(fixture):
            agent = SB.agentmemory_write(observation.scope, run=run)["agentId"]
            payload = {**A.remember_arguments(observation, agent), "agentId": agent}
            A.assert_public_only(payload)
            g13.request_json(base, "/agentmemory/remember", body=payload)
            time.sleep(0.05)
            for row in g33.native_rows(base, agent):
                for source in (row.get("sourceObservationIds") or []):
                    native[row.get("id")] = source
        for case in cases_for(fixture):
            agent = SB.agentmemory_query(case.scope, run=run)["agentId"]
            arguments = {**A.search_arguments(case, agent, LIMIT), "agentId": agent}
            raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
            items = []
            for rank, hit in enumerate((raw.get("results") or [])[:LIMIT], start=1):
                canonical = (native.get(hit.get("obsId"))
                             or (hit.get("sourceObservationIds") or [None])[0])
                exact = canonical in {o.id for o in fixture.observations}
                items.append({"native_rank": rank,
                              "canonical_id": canonical if exact else None,
                              "provenance_exact": exact})
            records.append({"case_id": case.id, "scope": case.scope,
                            "bound_identity": agent, "returned": items})
    finally:
        for agent_launcher in launchers.values():
            try:
                g13.stop_service(g33.AGENTMEMORY, state, repetition,
                                 SB.agentmemory_write(scopes[0], run=run)["agentId"],
                                 agent_launcher)
            except Exception:
                pass
    return records


ENGINES = {"mem0": run_mem0, "agentmemory": run_agentmemory}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=sorted(ENGINES))
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()

    fixture = L.build_longitudinal_fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"gen78-{args.engine}-"))
    repetitions = []
    for repetition in range(1, args.repetitions + 1):
        records = score(fixture, ENGINES[args.engine](fixture, repetition, root))
        repetitions.append({"repetition": repetition, "records": records})
        collapses = sum(1 for r in records if r["scope_collapse"])
        print(f"{args.engine} rep{repetition}: {collapses}/{len(records)} scope_collapse",
              flush=True)

    (OUT / f"{args.engine}.json").write_text(json.dumps({
        "engine": args.engine, "generation": 78,
        "ablation": "frozen Gen77 scope binding replaces the Round-2 constant "
                    "namespace; one variable moved",
        "cases": list(CROSS_SCOPE_CASES),
        "ingestion": "prefix of the queried checkpoint only; the whole timeline "
                     "would charge future_leakage as a runner artefact",
        "excluded": {"LQ03": "same scope, different configuration - excluded so "
                             "configuration_collapse is not conflated with scope"},
        "binding": {k: v for k, v in SB.BINDINGS[args.engine].items()
                    if k not in ("write", "query")},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "scope_collapse_total": sum(1 for rep in repetitions
                                    for r in rep["records"] if r["scope_collapse"]),
        "case_runs": sum(len(rep["records"]) for rep in repetitions),
    }, indent=2, sort_keys=True, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
