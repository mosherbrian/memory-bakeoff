#!/usr/bin/env python3
"""Gen99: the replication run, on frozen `interference-v2`.

Unchanged Gen96 adapters, unchanged scorer, unchanged engine functions - only the
fixture grows to four independent cores. 4 cores x 4 loads x 3 repetitions.

No tuning. No core pooling. No cross-engine total. The Q1-Q3 verdict rules were
frozen in Gen98 and are read, not rewritten.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import interference as ITF          # noqa: E402
from memory_bakeoff import interference_v2 as V2        # noqa: E402
from memory_bakeoff import round3_adapters as R3        # noqa: E402

OUT = ROOT / "results" / "replication_gen99"
LIMIT = 5
HINDSIGHT_MAX_TOKENS = 4096
REPETITIONS = (1, 2, 3)


def gen97():
    loader = SourceFileLoader("gen97_runner",
                              str(ROOT / "scripts" / "run_gen97_interference.py"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    # The only change: cases ingest THEIR OWN core's records.
    module.VISIBLE_IDS = V2.visible_ids
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    runner = gen97()
    engine = args.engine
    expressible = R3.BUDGET_SURFACE[engine]["window_expressible"]
    fixture = V2.build_fixture()
    root = Path(args.root or tempfile.mkdtemp(prefix=f"gen99-{engine}-",
                                              dir="/private/tmp"))
    rows = []
    for case in fixture.cases:
        for repetition in REPETITIONS:
            started = time.perf_counter()
            returned, arguments = runner.ENGINES[engine](fixture, case, repetition,
                                                         root)
            latency = (time.perf_counter() - started) * 1000
            ids = [i for i in returned if i]
            if returned and not ids:
                raise SystemExit(
                    f"{case.id} rep{repetition}: {len(returned)} hits and NONE "
                    "mapped. Provenance failure in the probe, not a result.")
            scored = ITF.score_case(fixture, case, ids, LIMIT,
                                    window_expressible=expressible)
            rows.append({"engine": engine, "core": case.core, "load": case.load,
                         "case": case.id, "repetition": repetition,
                         "raw_returned": returned, "unmapped": returned.count(None),
                         "latency_ms": round(latency, 1), **scored})
            print(f"  {case.core:<18} L{case.load:<3} rep{repetition}  "
                  f"{scored['mechanisms']}")

    payload = {"engine": engine, "fixture_version": V2.FIXTURE_VERSION,
               "scorer_version": V2.SCORER_VERSION,
               "fixture_contract_sha256": V2.contract_sha256(),
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
