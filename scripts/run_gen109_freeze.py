#!/usr/bin/env python3
"""Gen109: freeze `reader-interference-v1`. Design only - nothing is executed.

No engine, model, reader, sidecar or GPU is invoked. This writes the frozen
fixture and contract under `immutable-evidence-v1` so the future run can consume
them unmodified and the hash proves they did not drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                      # noqa: E402
from memory_bakeoff import reader_interference as R            # noqa: E402

GENERATION = 109


def main() -> int:
    fixture = R.build_fixture()
    payload = {
        "contract_version": R.CONTRACT_VERSION,
        "contract_sha256": R.contract_hash(),
        "status": "FROZEN_UNRUN",
        "reader_question_state": "OPEN - this generation is NOT a reader result",
        "conditions": list(R.CONDITIONS),
        "decisions": list(R.DECISIONS),
        "grades": list(R.GRADES),
        "questions": list(R.QUESTIONS),
        "across_core_verdicts": list(R.ACROSS_CORE_VERDICTS),
        "execution_boundary": R.EXECUTION_BOUNDARY,
        "gen85": R.GEN85_STATUS,
        "parser_fixtures": list(R.PARSER_FIXTURES),
        "fixture": fixture,
    }
    # Guards before the write: a bad contract must never reach disk.
    R.assert_no_outcome_pooling(payload)
    R.assert_no_gen85_influence(payload)
    for core in fixture["cores"]:
        pair = [c for c in fixture["cases"]
                if c["core"] == core and c["condition"] in R.CONFLICT_PAIR]
        R.assert_conflict_pair_differs_only_in_order(*pair)

    out = EV.next_attempt(ROOT, GENERATION)
    path = EV.write_evidence(out, "reader_interference_v1.json", payload)
    verified = EV.verify(out)
    print(f"wrote {path}")
    print(f"contract sha256: {R.contract_hash()}")
    print(f"verify         : {verified}")
    if not verified["verified"]:
        raise SystemExit("manifest does not verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
