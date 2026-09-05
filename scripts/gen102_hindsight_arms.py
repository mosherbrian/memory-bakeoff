#!/usr/bin/env python3
"""Gen97 hindsight: all four load levels, three repetitions, one live service.

Hindsight expresses `max_tokens`, not a result count (Gen96), so
`window_expressible=False`: the target is reported present or absent and the
forgetting / displacement attribution is NOT_DEMONSTRABLE rather than inferred.
"""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV
from memory_bakeoff import interference as ITF
from memory_bakeoff import interference_v3 as V3                        # noqa: E402
from memory_bakeoff import round3_adapters as R3                      # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB        # noqa: E402

MAX_TOKENS = 4096
LIMIT = 5          # the harness reference only; never sent to the engine
REPETITIONS = (1, 2, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--arm", choices=("off", "on"), required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from hindsight_client import Hindsight
    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")
    fixture = V3.build_fixture()
    rows = []
    for case in fixture.cases:
        for repetition in REPETITIONS:
            bank = f"{args.run}-{case.id.lower()}-r{repetition}"
            native = {}
            for observation in ITF.ordered_observations(
                    fixture, case, V3.visible_ids):
                # The document id is SENT, not read back - the frozen Round-2
                # convention. A map keyed on a fabricated fallback matches
                # nothing, which is how the first attempt reported every hit
                # unmapped and every target absent.
                document_id = f"record-{observation.id}"
                client.retain(
                    bank_id=bank, content=observation.text,
                    document_id=document_id,
                    metadata={"record_id": observation.id,
                              "scope": observation.scope,
                              "configuration": observation.configuration},
                    tags=CB.hindsight_write(observation.configuration)["tags"])
                native[document_id] = observation.id
            if args.arm == "on":
                superseded = next(o for o in fixture.observations
                                  if o.core == case.core and o.role == "superseded")
                listed = client.list_memories(bank_id=bank, limit=200)
                units = getattr(listed, "items", None) or []
                # list_memories returns plain dicts, not objects; getattr on a
                # dict silently yields None, which is how the first attempt
                # "found" nothing. Read them as dicts.
                target = None
                for unit in units:
                    get = unit.get if isinstance(unit, dict) else (
                        lambda k: getattr(unit, k, None))
                    meta = get("metadata") or {}
                    marker = meta.get("record_id") if isinstance(meta, dict) else None
                    if marker is None:
                        marker = (get("document_id") or "").replace("record-", "") or None
                    if marker == superseded.id:
                        target = get("id") or get("memory_id") or get("memory_unit_id")
                        break
                if target is None:
                    raise SystemExit(
                        f"{case.id}: could not locate the superseded memory unit to "
                        "invalidate; refusing to report an ON arm that did nothing.")
                client.memory.update_memory(
                    bank_id=bank, memory_id=target,
                    update_memory_request={"state": "invalidated",
                                           "reason": "benchmark: superseded by the "
                                                     "later observation"})
            arguments = {"bank_id": bank, "query": case.query,
                         "max_tokens": MAX_TOKENS,
                         **CB.hindsight_query(case.configuration)}
            started = time.perf_counter()
            raw = client.recall(**arguments)
            latency = (time.perf_counter() - started) * 1000
            got = getattr(raw, "results", None)
            if got is None and isinstance(raw, dict):
                got = raw.get("results") or []
            returned = []
            for hit in (got or []):
                get = (lambda k: hit.get(k)) if isinstance(hit, dict) \
                    else (lambda k: getattr(hit, k, None))
                metadata = get("metadata") or {}
                marker = metadata.get("record_id") if isinstance(metadata, dict) else None
                canonical = native.get(get("document_id"))
                returned.append(canonical if canonical is not None and marker == canonical
                                else None)
            ids = [i for i in returned if i]
            if returned and not ids:
                raise SystemExit(
                    f"L{case.load} rep{repetition}: {len(returned)} hits and NONE "
                    "mapped to a canonical id. That is a provenance failure in the "
                    "probe, not a result - refusing to record 'target absent'.")
            scored = ITF.score_case(fixture, case, ids, LIMIT,
                                    window_expressible=False)
            rows.append({"engine": "hindsight", "core": case.core, "load": case.load, "case": case.id,
                         "repetition": repetition,
                         "arm": args.arm, "core": case.core,
                         "requested": f"max_tokens={MAX_TOKENS}",
                         "raw_returned": returned, "returned_count": len(returned),
                         "unmapped": returned.count(None),
                         "latency_ms": round(latency, 1),
                         "arguments": {k: v for k, v in arguments.items()
                                       if k != "query"},
                         **scored})
            print(f"  {case.core:<18} L{case.load:<3} rep{repetition} n={len(returned)} "
                  f"{scored['mechanisms']}")

    payload = {"engine": "hindsight", "arm": args.arm, "fixture_version": V3.FIXTURE_VERSION,
               "scorer_version": V3.SCORER_VERSION,
               "budget": R3.BUDGET_SURFACE["hindsight"],
               "saturation": R3.saturation_meaning("hindsight"),
               "rows": rows}
    R3.assert_within_engine_only(payload)
    out = Path(args.out)
    EV.write_evidence(out.parent, out.name, payload)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
