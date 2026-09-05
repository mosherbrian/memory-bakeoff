"""Gen89: decompose the current_truth row. No engine runs."""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import current_truth_audit as audit
from memory_bakeoff.longitudinal import build_longitudinal_fixture, score_longitudinal_case

RESULT_DIRS = {
    "perseus": "perseus_vault_gen29_longitudinal",
    "mem0": "mem0_gen32_longitudinal",
    "hindsight": "hindsight_gen31_longitudinal",
    "agentmemory": "agentmemory_gen33_longitudinal",
}


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    cases = {c.id: c for c in fixture.cases if c.id in audit.CASES}
    expected = {c: cases[c].expected_ids for c in audit.CASES}
    prohibited = {c: cases[c].prohibited_ids for c in audit.CASES}

    records: dict[str, dict[str, list]] = {c: {} for c in audit.CASES}
    pooled = {}
    for engine, directory in RESULT_DIRS.items():
        clean = total = 0
        for repetition in (1, 2, 3):
            data = json.loads(
                (root / "results" / directory / f"repetition-{repetition}.json").read_text())
            for row in data["cases"]:
                if row["case_id"] not in audit.CASES:
                    continue
                total += 1
                if not row["failure_classes"]:
                    clean += 1
                records[row["case_id"]].setdefault(engine, []).append(
                    [item["canonical_id"] for item in row["returned"]])
        pooled[engine] = f"{clean}/{total}"

    decomposition = audit.decompose(records, expected, prohibited)
    payload = {
        "contract": audit.contract(),
        "controls": audit.controls(score_longitudinal_case, fixture, cases),
        "purity_audit": audit.purity_audit(),
        "pooled_counts_being_replaced": pooled,
        **decomposition,
    }
    destination = root / "results" / "current_truth_gen89"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "decomposition.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print("pooled counts being replaced:", pooled)
    print("mechanism totals:", json.dumps(decomposition["mechanism_totals"], indent=1))
    for case in audit.CASES:
        per = {r["engine"]: r["mechanism"] for r in decomposition["rows"]
               if r["case"] == case and r["repetition"] == 1}
        print(f"  {case}: {per}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
