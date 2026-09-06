#!/usr/bin/env python3
"""Gen114: grade the sealed attempt once, with the frozen v4 ruler."""
from __future__ import annotations

import collections, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                          # noqa: E402
from memory_bakeoff import reader_interference_v4 as V4            # noqa: E402

ATTEMPT = ROOT / "results" / "gen114" / "attempt1"


def main() -> int:
    responses = [json.loads(l) for l in (ATTEMPT / "reader_responses.jsonl").read_text().splitlines()]
    requests = {json.loads(l)["call_index"]: json.loads(l)
                for l in (ATTEMPT / "reader_requests.jsonl").read_text().splitlines()}
    cases = {c["id"]: c for c in V4.build_fixture()["cases"]}
    if len(responses) != 60 or len({r["call_index"] for r in responses}) != 60:
        raise SystemExit("FAIL CLOSED: schedule accounting is wrong")

    rows = []
    for response in responses:
        case = cases[response["case_id"]]
        parsed = V4.parse_response(response["text"])
        graded = V4.grade(parsed, case)
        expected = V4.CONTROL_RULE["expected"].get(response["condition"])
        rows.append({
            "call_index": response["call_index"], "case_id": response["case_id"],
            "core": response["core"], "condition": response["condition"],
            "repetition": response["repetition"],
            "request_fingerprint": requests[response["call_index"]]["request_fingerprint"],
            "response_sha256": response["response_sha256"],
            "terminal_disposition": response["terminal_disposition"],
            "parse_status": parsed["parse_status"],
            "answer": parsed["answer"], "citations": list(parsed["citations"]),
            "answer_class": graded["answer_class"],
            "citation_relation": graded["citation_relation"],
            "outcome": graded["outcome"], "why": graded["why"],
            "control_pass": (expected is not None and graded["outcome"] == expected),
        })

    cores = sorted({r["core"] for r in rows})
    gates = {}
    for core in cores:
        cells = [r for r in rows if r["core"] == core
                 and r["condition"] in V4.CONTROL_CONDITIONS]
        passing = sum(r["control_pass"] for r in cells)
        gates[core] = {"control_cells": len(cells), "passing": passing,
                       "interpretable": len(cells) == 9 and passing == 9}

    questions = {}
    for core in cores:
        if not gates[core]["interpretable"]:
            questions[core] = {"Q1": "NOT_INTERPRETABLE", "Q2": "NOT_INTERPRETABLE",
                               "Q3": "NOT_INTERPRETABLE"}
            continue
        def count(condition):
            cells = [r for r in rows if r["core"] == core and r["condition"] == condition]
            return sum(r["outcome"] in (V4.OUTCOMES[1], V4.OUTCOMES[2]) for r in cells)
        clean = count("CLEAN_CURRENT")
        stale_first = count("CONFLICT_STALE_FIRST")
        current_first = count("CONFLICT_CURRENT_FIRST")
        dist = {c: collections.Counter(
            r["outcome"] for r in rows if r["core"] == core and r["condition"] == c)
            for c in V4.CONFLICT_PAIR}
        conflicts = [r for r in rows if r["core"] == core and r["condition"] in V4.CONFLICT_PAIR]
        questions[core] = {
            "Q1": {"clean_current_bad": clean, "stale_first_bad": stale_first,
                   "current_first_bad": current_first,
                   "effect": stale_first > clean or current_first > clean},
            "Q2": {"distributions_differ": dist[V4.CONFLICT_PAIR[0]] != dist[V4.CONFLICT_PAIR[1]],
                   "stale_first": dict(dist[V4.CONFLICT_PAIR[0]]),
                   "current_first": dict(dist[V4.CONFLICT_PAIR[1]])},
            "Q3": {"all_conflict_cells_correct_current":
                   all(r["outcome"] == V4.OUTCOMES[0] for r in conflicts)},
        }

    all_interpretable = all(g["interpretable"] for g in gates.values())
    if all_interpretable:
        effect_cores = [c for c in cores if questions[c]["Q1"]["effect"]]
        q4 = {4: "REPLICATED_ACROSS_CORES", 3: "PARTIAL_REPLICATION",
              2: "PARTIAL_REPLICATION", 1: "FIXTURE_SPECIFIC",
              0: "NO_EFFECT"}[len(effect_cores)]
    else:
        q4 = V4.NOT_INTERPRETABLE
        effect_cores = []

    EV.write_evidence(ATTEMPT, "reader_interference_results.json", {
        "generation": 114, "evidence_class": "controlled_reader_interference",
        "contract_sha256": V4.contract_hash(),
        "scope_note": "Controls which benchmark-owned records the reader sees. "
                      "Does NOT establish that any memory product supplies this "
                      "context or this order. Not raw-product or full-product "
                      "evidence.",
        "planned_calls": 60,
        "completed": sum(r["terminal_disposition"] == "COMPLETED" for r in rows),
        "control_gates": gates, "questions": questions,
        "Q4": q4, "Q4_effect_cores": effect_cores,
        "Q5_parser_gate": "matched v4 before execution",
        "Q6_prompt_gate": "matched v4 before execution",
        "cells": rows,
    })

    print(f"{'core':<20}{'controls':>10}{'interpretable':>15}")
    for core in cores:
        g = gates[core]
        print(f"{core:<20}{g['passing']}/{g['control_cells']:<8}{str(g['interpretable']):>15}")
    print("\noutcome counts by condition:")
    for condition in V4.CONDITIONS:
        counter = collections.Counter(r["outcome"] for r in rows if r["condition"] == condition)
        print(f"   {condition:<32}{dict(counter)}")
    print(f"\nQ4: {q4}")
    print(f"manifest: {EV.verify(ATTEMPT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
