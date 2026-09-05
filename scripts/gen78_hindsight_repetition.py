#!/usr/bin/env python3
"""Gen78 hindsight repetition: one bank per scope, the frozen Gen77 binding.

Mirrors gen70_hindsight_repetition.py except that `bank_id` is bound to the
observation's scope rather than to the run, and only the two genuinely
cross-scope cases are asked.
"""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                      # noqa: E402
from memory_bakeoff.providers import hindsight_longitudinal as H   # noqa: E402
from memory_bakeoff.providers import scope_bound as SB             # noqa: E402

LIMIT = 5
CROSS_SCOPE_CASES = ("LQ08", "LQ09")


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
    cases = [c for c in fixture.cases if c.id in CROSS_SCOPE_CASES]
    checkpoint = {c.checkpoint_id for c in cases}
    if len(checkpoint) != 1:
        raise SystemExit("cross-scope cases span checkpoints")
    prefix = fixture.prefix(next(iter(checkpoint)))

    client = Hindsight(base_url=f"http://127.0.0.1:{args.port}")
    native = {}
    for observation in prefix:
        bank = SB.hindsight_write(observation.scope, run=args.run)["bank_id"]
        payload = H.retain_arguments(observation, bank)
        H.assert_public_only(payload)
        client.retain(**payload)
        native[payload["document_id"]] = observation.id
        time.sleep(0.05)

    records = []
    for case in cases:
        bank = SB.hindsight_query(case.scope, run=args.run)["bank_id"]
        arguments = H.recall_arguments(case, bank, LIMIT)
        raw = client.recall(**arguments)
        records.append({"case_id": case.id, "scope": case.scope,
                        "bound_identity": bank,
                        "returned": result_rows(raw, native)})

    Path(args.out).write_text(json.dumps(
        {"repetition": args.repetition, "records": records}, indent=2,
        sort_keys=True, default=str) + "\n")
    print(f"hindsight rep{args.repetition}: {len(records)} cross-scope cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
