#!/usr/bin/env python3
"""Gen80 hindsight repetition: tags carry configuration, bank_id still carries scope."""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                       # noqa: E402
from memory_bakeoff.providers import hindsight_longitudinal as H    # noqa: E402
from memory_bakeoff.providers import scope_bound as SB              # noqa: E402
from memory_bakeoff.providers import configuration_bound as CB      # noqa: E402

LIMIT = 5
CASE = "LQ03"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from hindsight_client import Hindsight
    from gen31_repetition import result_rows

    fixture = L.build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.id == CASE)
    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")

    native = {}
    for observation in fixture.prefix(case.checkpoint_id):
        bank = SB.hindsight_write(observation.scope, run=args.run)["bank_id"]
        payload = H.retain_arguments(observation, bank)
        H.assert_public_only(payload)
        payload = {**payload, **CB.hindsight_write(observation.configuration)}
        client.retain(**payload)
        native[payload["document_id"]] = observation.id
        time.sleep(0.05)

    bank = SB.hindsight_query(case.scope, run=args.run)["bank_id"]
    arguments = {**H.recall_arguments(case, bank, LIMIT),
                 **CB.hindsight_query(case.configuration)}
    raw = client.recall(**arguments)
    record = {"case_id": CASE, "scope": case.scope,
              "configuration": case.configuration,
              "bound_scope": bank,
              "bound_configuration": arguments["tags"][0],
              "returned": result_rows(raw, native)}

    Path(args.out).write_text(json.dumps(
        {"repetition": args.repetition, "records": [record]}, indent=2,
        sort_keys=True, default=str) + "\n")
    print(f"hindsight rep{args.repetition}: recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
