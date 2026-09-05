"""Gen90: replay the four pure current-truth cases through prefix windows 1..5."""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import window_ablation as ablation
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
    cases = {c.id: c for c in fixture.cases if c.id in ablation.PURE_CASES}

    rows = []
    for engine, directory in RESULT_DIRS.items():
        for repetition in (1, 2, 3):
            data = json.loads(
                (root / "results" / directory / f"repetition-{repetition}.json").read_text())
            for record in data["cases"]:
                if record["case_id"] not in ablation.PURE_CASES:
                    continue
                returned = [item["canonical_id"] for item in record["returned"]]
                result = ablation.curve(score_longitudinal_case, fixture,
                                        cases[record["case_id"]], returned)
                for point in result["points"]:
                    ablation.assert_truncation_only(returned, point["returned"])
                rows.append({"engine": engine, "repetition": repetition,
                             "case": record["case_id"], "returned": returned,
                             **result})

    payload = {"contract": ablation.contract(),
               "summary": ablation.summarise(rows), "rows": rows}
    destination = root / "results" / "window_ablation_gen90"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "curve.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print(json.dumps(payload["summary"], indent=1))
    print("\nper case/engine/repetition:")
    for row in rows:
        if row["verdict"] != ablation.ALREADY_CLEAN:
            print(f"  {row['case']} {row['engine']:12s} rep{row['repetition']} "
                  f"{row['verdict']:16s} clean at k={row['clean_windows']} "
                  f"order={row['returned']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
