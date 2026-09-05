#!/usr/bin/env python3
"""Gen102: does telling an engine that one fact supersedes another remove the stale co-return?

Paired arms on the IDENTICAL corrected fixture (`interference-v3`) for perseus,
mem0 and hindsight: lifecycle OFF versus the frozen Gen101 binding ON.

agentmemory runs ONE arm only. Its supersession is automatic, so an "OFF" arm
would be a configuration the product does not offer - a manufactured comparison.

The three mechanism kinds stay separate. No supersession score.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF                    # noqa: E402
from memory_bakeoff import interference_v3 as V3                  # noqa: E402
from memory_bakeoff import round3_adapters as R3                  # noqa: E402
from memory_bakeoff import supersession_binding as SB             # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB    # noqa: E402
from memory_bakeoff.providers import scope_bound as SBIND         # noqa: E402

OUT = ROOT / "results" / "supersession_ablation_gen102"
LIMIT = 5
HINDSIGHT_MAX_TOKENS = 4096
REPETITIONS = (1, 2, 3)
SINGLE_ARM = {"agentmemory"}


def gen97():
    loader = SourceFileLoader("gen97_runner",
                              str(ROOT / "scripts" / "run_gen97_interference.py"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    module.VISIBLE_IDS = V3.visible_ids          # corrected chronology
    return module


def roles(fixture, case):
    current = next(o for o in fixture.observations
                   if o.core == case.core and o.role == "current")
    superseded = next(o for o in fixture.observations
                      if o.core == case.core and o.role == "superseded")
    return current, superseded


# --- perseus: EXPLICIT_LINEAGE -------------------------------------------
def run_perseus(fixture, case, repetition, root, binding_on):
    g29 = gen97().load("run_perseus_gen29_longitudinal")
    home = root / f"{case.id}-rep{repetition}"
    home.mkdir(parents=True, exist_ok=True)
    db, key = home / "vault.sqlite", home / "vault.key"
    g29.sh([g29.BIN, "keygen", "--key-file", key])
    native = {}
    runner = gen97()
    for observation in runner.observations_for(fixture, case):
        body = runner.public_body(observation)
        receipt = json.loads(g29.sh(
            [g29.BIN, "write", "--db", db, "--encryption-key", key,
             "--category", CB.perseus_write(observation.configuration)["category"],
             "--key", f"record-{observation.id}",
             "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
             "--workspace-hash", SBIND.scope_token(observation.scope)]))
        native[receipt["id"]] = observation.id
    server = g29.Server(db, key)
    lifecycle = None
    try:
        if binding_on:
            current, superseded = roles(fixture, case)
            category = CB.perseus_write(case.configuration)["category"]
            lifecycle = server.rpc("tools/call", {
                "name": "perseus_vault_supersede",
                "arguments": {"from_category": category,
                              "from_key": f"record-{current.id}",
                              "to_category": category,
                              "to_key": f"record-{superseded.id}",
                              "relationship": "supersedes",
                              "reason": "benchmark: the later observation replaces "
                                        "the earlier"}})
        arguments = {"query": case.query, "limit": LIMIT, "mode": "hybrid",
                     "workspace_hash": SBIND.scope_token(case.scope),
                     **CB.perseus_query(case.configuration)}
        payload = server.recall(arguments)
        returned = [native.get(h.get("id")) for h in payload.get("items", [])[:LIMIT]]
    finally:
        server.stop()
    return returned, {"binding_on": binding_on, "lifecycle_call": bool(lifecycle)}


# --- mem0: PRODUCT_DECIDES ------------------------------------------------
def run_mem0(fixture, case, repetition, root, binding_on):
    runner = gen97()
    g32 = runner.load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    memory = Memory.from_config(g32.config_for(
        str(root / f"{case.id}-rep{repetition}"),
        f"bakeoff-{case.id.lower()}-r{repetition}"))
    native = {}
    for observation in runner.observations_for(fixture, case):
        result = memory.add(
            observation.text,
            user_id=SBIND.mem0_write(observation.scope)["user_id"],
            agent_id=CB.mem0_write(observation.configuration)["agent_id"],
            infer=bool(binding_on),
            metadata={"record_id": observation.id})
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native[row["id"]] = observation.id
    filters = R3.merge_payloads(SBIND.mem0_query(case.scope),
                               CB.mem0_query(case.configuration))["filters"]
    raw = memory.search(case.query, filters=filters, limit=LIMIT,
                        threshold=g32.M.THRESHOLD)
    hits = raw.get("results") if isinstance(raw, dict) else raw
    returned = []
    for hit in (hits or [])[:LIMIT]:
        marker = (hit.get("metadata") or {}).get("record_id")
        canonical = native.get(hit.get("id"))
        returned.append(canonical if canonical is not None and marker == canonical else None)
    return returned, {"binding_on": binding_on, "infer": bool(binding_on)}


ENGINES = {"perseus": run_perseus, "mem0": run_mem0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--arm", choices=("off", "on"), required=True)
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    engine, binding_on = args.engine, args.arm == "on"
    if engine in SINGLE_ARM and binding_on is False:
        raise SystemExit(
            f"{engine} has an automatic mechanism; an OFF arm is a configuration the "
            "product does not offer and would be a manufactured comparison.")
    fixture = V3.build_fixture()
    root = Path(args.root or tempfile.mkdtemp(prefix=f"gen102-{engine}-{args.arm}-",
                                              dir="/private/tmp"))
    runner = gen97()
    rows = []
    for case in fixture.cases:
        for repetition in REPETITIONS:
            fn = ENGINES.get(engine)
            if fn is None:                       # agentmemory: unchanged native path
                returned, arguments = runner.ENGINES[engine](fixture, case,
                                                             repetition, root)
                arguments = {"binding_on": "native, unchanged"}
            else:
                returned, arguments = fn(fixture, case, repetition, root, binding_on)
            ids = [i for i in returned if i]
            if returned and not ids:
                raise SystemExit(f"{case.id} rep{repetition}: hits returned and none "
                                 "mapped - provenance failure, not a result.")
            current, superseded = roles(fixture, case)
            scored = ITF.score_case(fixture, case, ids, LIMIT,
                                    window_expressible=R3.BUDGET_SURFACE[engine]
                                    ["window_expressible"])
            rows.append({
                "engine": engine, "arm": args.arm, "core": case.core,
                "load": case.load, "case": case.id, "repetition": repetition,
                "mechanism_kind": SB.BINDINGS[engine]["kind"],
                "superseded_retrievable": superseded.id in ids,
                "current_retrievable": current.id in ids,
                "current_rank": (ids.index(current.id) + 1) if current.id in ids else None,
                "arguments": arguments, **scored})
            print(f"  {case.core:<18} L{case.load:<3} rep{repetition}  "
                  f"stale={superseded.id in ids} current={current.id in ids} "
                  f"{scored['mechanisms']}")

    payload = {"engine": engine, "arm": args.arm,
               "mechanism_kind": SB.BINDINGS[engine]["kind"],
               "fixture_version": V3.FIXTURE_VERSION,
               "fixture_contract_sha256": V3.contract_sha256(),
               "binding": SB.BINDINGS[engine], "rows": rows}
    R3.assert_within_engine_only(payload)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{engine}-{args.arm}.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(f"\nwrote {OUT / (engine + '-' + args.arm + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
