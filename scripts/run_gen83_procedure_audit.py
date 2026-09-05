"""Gen83: audit the recommended_procedure axis end to end. No engine runs.

Reads the committed Round-2 records for LQ10, exercises the frozen scorer with
constructed controls, and writes the audit payload.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import procedure_reachability as audit
from memory_bakeoff.longitudinal import build_longitudinal_fixture, score_longitudinal_case

RESULT_DIRS = {
    "perseus": "perseus_vault_gen29_longitudinal",
    "hindsight": "hindsight_gen31_longitudinal",
    "mem0": "mem0_gen32_longitudinal",
    "agentmemory": "agentmemory_gen33_longitudinal",
}


def committed_windows(root: pathlib.Path) -> dict[str, list[dict]]:
    """Re-read LQ10 from the committed records rather than trusting the table."""
    out: dict[str, list[dict]] = {}
    for engine, directory in RESULT_DIRS.items():
        rows = []
        for repetition in (1, 2, 3):
            path = root / "results" / directory / f"repetition-{repetition}.json"
            case = next(c for c in json.loads(path.read_text())["cases"]
                        if c["case_id"] == audit.CASE_ID)
            ids = [item["canonical_id"] for item in case["returned"]]
            rows.append({
                "repetition": repetition,
                "limit": case["requested_limit"],
                "returned": ids,
                "failure_classes": case["failure_classes"],
                "expected_rank": ids.index(audit.EXPECTED) + 1 if audit.EXPECTED in ids else None,
                "prohibited_rank": ids.index(audit.PROHIBITED) + 1 if audit.PROHIBITED in ids else None,
            })
        out[engine] = rows
    return out


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.id == audit.CASE_ID)
    windows = committed_windows(root)
    payload = {
        "contract": audit.verdict(),
        "controls": audit.controls(score_longitudinal_case, fixture, case),
        "discriminability": audit.discriminability(fixture, case.query),
        "window_pressure": audit.window_pressure(
            len(fixture.prefix(audit.CHECKPOINT_ID)), windows["perseus"][0]["limit"]),
        "committed_windows": windows,
        "attribution": audit.attribution(),
    }
    destination = root / "results" / "procedure_audit_gen83"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "audit.json").write_text(json.dumps(payload, indent=1, sort_keys=True))
    print(json.dumps(payload["attribution"], indent=1))
    print(json.dumps(payload["contract"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
