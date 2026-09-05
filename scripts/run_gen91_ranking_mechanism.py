"""Gen91: why the stale record ranks first. No engine runs."""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import ranking_mechanism as mech

RESULT_DIRS = {
    "perseus": "perseus_vault_gen29_longitudinal",
    "mem0": "mem0_gen32_longitudinal",
    "hindsight": "hindsight_gen31_longitudinal",
    "agentmemory": "agentmemory_gen33_longitudinal",
}
# The nine no-prefix ranking failures Gen90 identified, by case and pair.
FAILURES = {
    "LQ11": {"stale": "L009", "current": "L010",
             "engines": {"perseus": (1, 3), "mem0": (1, 2, 3), "hindsight": (1, 2, 3)}},
    "LQ14": {"stale": "L012", "current": "L014", "engines": {"perseus": (1,)}},
}


def hit_score(item):
    scores = item.get("scores")
    if isinstance(scores, dict):
        return scores.get("final"), scores
    return item.get("score"), None


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    rows, components = [], []
    for case, spec in FAILURES.items():
        for engine, repetitions in spec["engines"].items():
            for repetition in repetitions:
                data = json.loads((root / "results" / RESULT_DIRS[engine] /
                                   f"repetition-{repetition}.json").read_text())
                record = next(c for c in data["cases"] if c["case_id"] == case)
                by_id = {}
                for item in record["returned"]:
                    value, parts = hit_score(item)
                    by_id[item["canonical_id"]] = (value, parts)
                stale, _ = by_id.get(spec["stale"], (None, None))
                current, _ = by_id.get(spec["current"], (None, None))
                others = [v for k, (v, _) in by_id.items()
                          if k not in (spec["stale"], spec["current"]) and v is not None]
                verdict = mech.classify(stale, current, others)
                rows.append({"case": case, "engine": engine, "repetition": repetition,
                             "stale_score": stale, "current_score": current,
                             "order": [i["canonical_id"] for i in record["returned"]],
                             **verdict})
                stale_parts = by_id.get(spec["stale"], (None, None))[1]
                current_parts = by_id.get(spec["current"], (None, None))[1]
                if stale_parts and current_parts and repetition == 1:
                    components.append({
                        "case": case, "engine": engine,
                        **mech.component_attribution(stale_parts, current_parts)})

    perseus_lq11 = {}
    for repetition in (1, 2, 3):
        data = json.loads((root / "results" / RESULT_DIRS["perseus"] /
                           f"repetition-{repetition}.json").read_text())
        record = next(c for c in data["cases"] if c["case_id"] == "LQ11")
        perseus_lq11[repetition] = [i["canonical_id"] for i in record["returned"]]

    payload = {
        "contract": mech.contract(),
        "rows": rows,
        "component_attribution": components,
        "perseus_flip_test": mech.perseus_flip_test(perseus_lq11, scores_observable=False),
        "mechanism_totals": {},
    }
    for row in rows:
        key = row["mechanism"]
        payload["mechanism_totals"][key] = payload["mechanism_totals"].get(key, 0) + 1

    destination = root / "results" / "ranking_mechanism_gen91"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "mechanism.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))

    print("mechanism totals:", payload["mechanism_totals"])
    for row in rows:
        share = row.get("share_of_field")
        share = f"{share:.1%}" if isinstance(share, float) else "n/a"
        print(f"  {row['case']} {row['engine']:10s} rep{row['repetition']} "
              f"{row['mechanism']:22s} pair gap share of field = {share}")
    print("\ncomponent attribution:")
    for entry in components:
        print(f"  {entry['engine']} {entry['case']}: dominant={entry['dominant_component']} "
              f"identical={entry['identical_components']}")
        print(f"    gaps={ {k: (round(v,6) if v is not None else None) for k,v in entry['component_gaps'].items()} }")
    print("\nperseus flip:", payload["perseus_flip_test"]["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
