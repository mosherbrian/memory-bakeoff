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

from memory_bakeoff import interference as ITF                        # noqa: E402
from memory_bakeoff import round3_adapters as R3                      # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB        # noqa: E402

MAX_TOKENS = 4096
LIMIT = 5          # the harness reference only; never sent to the engine
REPETITIONS = (1, 2, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from hindsight_client import Hindsight
    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")
    fixture = ITF.build_fixture()
    rows = []
    for case in fixture.cases:
        for repetition in REPETITIONS:
            bank = f"{args.run}-l{case.load}-r{repetition}"
            visible = set(ITF.visible_ids(fixture, case))
            native = {}
            for observation in fixture.observations:
                if observation.id not in visible:
                    continue
                result = client.retain(
                    bank_id=bank, content=observation.text,
                    metadata={"record_id": observation.id,
                              "scope": observation.scope,
                              "configuration": observation.configuration},
                    tags=CB.hindsight_write(observation.configuration)["tags"])
                document_id = getattr(result, "document_id", None) or \
                    f"record-{observation.id}"
                native[document_id] = observation.id
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
            scored = ITF.score_case(fixture, case, ids, LIMIT,
                                    window_expressible=False)
            rows.append({"engine": "hindsight", "load": case.load, "case": case.id,
                         "repetition": repetition,
                         "requested": f"max_tokens={MAX_TOKENS}",
                         "raw_returned": returned, "returned_count": len(returned),
                         "unmapped": returned.count(None),
                         "latency_ms": round(latency, 1),
                         "arguments": {k: v for k, v in arguments.items()
                                       if k != "query"},
                         **scored})
            print(f"  L{case.load:<3} rep{repetition}  n={len(returned)}  "
                  f"{scored['mechanisms']}")

    payload = {"engine": "hindsight", "fixture_version": ITF.FIXTURE_VERSION,
               "scorer_version": ITF.SCORER_VERSION,
               "budget": R3.BUDGET_SURFACE["hindsight"],
               "saturation": R3.saturation_meaning("hindsight"),
               "rows": rows}
    R3.assert_within_engine_only(payload)
    Path(args.out).write_text(json.dumps(payload, indent=1, sort_keys=True,
                                         default=str))
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
