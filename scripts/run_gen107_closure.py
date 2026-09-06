#!/usr/bin/env python3
"""Gen107: write the Round 3 closure artifact under `immutable-evidence-v1`.

No engine runs. Deterministic summary of committed evidence only. The write
refuses to overwrite an existing attempt, which is the whole point of the
contract Gen106 added after Gen105 destroyed the pre-correction cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                    # noqa: E402
from memory_bakeoff import round3_closure as C               # noqa: E402

GENERATION = 107


def main() -> int:
    payload = C.closure_payload()
    # Guards run BEFORE the write: a bad artefact must never reach disk.
    C.assert_no_pooled_mechanism_score(payload)
    C.assert_gen102_is_superseded(payload)
    C.assert_legacy_not_called_verified(payload["source_registry"])
    C.assert_v1_v2_not_retracted(payload)

    out = EV.next_attempt(ROOT, GENERATION)
    path = EV.write_evidence(out, "round3_closure.json", payload)
    verified = EV.verify(out)
    print(f"wrote {path}")
    print(f"manifest: {out / EV.MANIFEST}")
    print(f"verify  : {verified}")
    if not verified["verified"]:
        raise SystemExit("manifest does not verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
