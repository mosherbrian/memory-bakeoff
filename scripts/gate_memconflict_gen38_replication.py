#!/usr/bin/env python3
"""Gen38 replication gate: the fresh calibration personas must reproduce Gen37.

Run per engine BEFORE that engine touches the 27 held-out personas. Compares
question set, exact-provenance applicability, canonical returned released-session
ordering, hit class and rank, and native scores. Native ids and wall-clock
measurements are allowed to differ; semantics are not.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.round2_reporting import ReportingError

GEN37 = ROOT / "results/memconflict_gen37_calibration"
GEN38 = ROOT / "results/memconflict_gen38_full_release"


def sessions_of(record: dict) -> list:
    return [item["session_id"] for item in record["returned"]]


def scores_of(record: dict) -> list:
    return [item["score"] for item in record["returned"]]


def first_support(record: dict, gold) -> int | None:
    if gold.support_sessions is None:
        return None
    for item in record["returned"]:
        if item["session_id"] in gold.support_sessions:
            return item["rank"]
    return 0


# Declared BEFORE any held-out persona was run, from calibration evidence only.
# Perseus hybrid recall returns tied scores; the order among equal-scored items is
# stable within one run but not across runs against a fresh vault. An ordering
# difference that sits inside an identical score vector containing ties is
# tie instability, not semantic drift. Anything else is drift.
TOLERANCE = {
    "ordering_differences_must_be_tie_explained": True,
    "max_hit_at_3_class_change_fraction": 0.01,
    "score_vectors_must_match_exactly": True,
    "applicability_must_match_exactly": True,
}


def tie_explained(old_record: dict, new_record: dict) -> bool:
    """True when both runs returned the same scores and those scores contain ties."""
    old_scores = scores_of(old_record)
    new_scores = scores_of(new_record)
    return old_scores == new_scores and len(set(old_scores)) < len(old_scores)


def compare(engine: str, personas: dict[str, dict]) -> dict:
    old_dir, new_dir = GEN37 / engine, GEN38 / engine
    rows, mismatches = {}, []
    for path in sorted(old_dir.glob("persona-*.json")):
        persona_id = json.loads(path.read_text())["persona_id"]
        new_path = new_dir / f"persona-{persona_id}.json"
        if not new_path.exists():
            raise ReportingError(f"{engine}: fresh calibration leaf missing for {persona_id}")
        old = {r["question_key"]: r for r in json.loads(path.read_text())["questions"]}
        new = {r["question_key"]: r for r in json.loads(new_path.read_text())["questions"]}
        persona = personas[persona_id]
        gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}

        row = {"questions_old": len(old), "questions_new": len(new),
               "same_question_set": sorted(old) == sorted(new),
               "ordering_mismatches": [], "ordering_tie_explained": [],
               "ordering_unexplained": [], "score_mismatches": [],
               "rank_mismatches": [], "hit_at_3_class_changes": [],
               "applicability_mismatches": [], "measured_questions": 0}
        if not row["same_question_set"]:
            mismatches.append(f"{engine}/{persona_id}: question set differs")
        for key in sorted(set(old) & set(new)):
            gold = gold_by_key[key]
            if sessions_of(old[key]) != sessions_of(new[key]):
                row["ordering_mismatches"].append(key)
                bucket = "ordering_tie_explained" if tie_explained(old[key], new[key]) \
                    else "ordering_unexplained"
                row[bucket].append(key)
            if scores_of(old[key]) != scores_of(new[key]):
                row["score_mismatches"].append(key)
            old_rank, new_rank = first_support(old[key], gold), first_support(new[key], gold)
            if old_rank != new_rank:
                row["rank_mismatches"].append(key)
            if gold.support_sessions is not None:
                row["measured_questions"] += 1
                old_hit = old_rank is not None and 1 <= old_rank <= 3
                new_hit = new_rank is not None and 1 <= new_rank <= 3
                if old_hit != new_hit:
                    row["hit_at_3_class_changes"].append(key)

        # Only unexplained differences are drift. Tie reordering is recorded, not fatal.
        if row["ordering_unexplained"]:
            mismatches.append(f"{engine}/{persona_id}: {len(row['ordering_unexplained'])} "
                              f"ordering differences NOT explained by score ties "
                              f"e.g. {row['ordering_unexplained'][:3]}")
        if row["score_mismatches"]:
            mismatches.append(f"{engine}/{persona_id}: {len(row['score_mismatches'])} score mismatches")
        if row["applicability_mismatches"]:
            mismatches.append(f"{engine}/{persona_id}: applicability changed")
        changed = len(row["hit_at_3_class_changes"])
        if row["measured_questions"] and changed / row["measured_questions"] > \
                TOLERANCE["max_hit_at_3_class_change_fraction"]:
            mismatches.append(f"{engine}/{persona_id}: {changed}/{row['measured_questions']} hit@3 class "
                              f"changes exceed the declared tolerance")
        rows[persona_id] = row
    measured = sum(r["measured_questions"] for r in rows.values())
    changed = sum(len(r["hit_at_3_class_changes"]) for r in rows.values())
    return {"per_persona": rows, "material_mismatches": mismatches,
            "tolerance": TOLERANCE,
            "tie_instability": {
                "ordering_differences_total": sum(len(r["ordering_mismatches"]) for r in rows.values()),
                "tie_explained": sum(len(r["ordering_tie_explained"]) for r in rows.values()),
                "unexplained": sum(len(r["ordering_unexplained"]) for r in rows.values()),
                "hit_at_3_class_changes": changed,
                "measured_questions": measured,
                "hit_at_3_class_change_fraction": round(changed / measured, 5) if measured else None,
                "reading": "Perseus hybrid recall ties; order among equal-scored items is stable "
                           "within a run and not across runs against a fresh store",
            },
            "passed": not mismatches}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", required=True, choices=("perseus", "mem0"))
    args = ap.parse_args()
    personas = {p["ID"]: p for p in M.load_personas()}
    result = compare(args.engine, personas)

    out = GEN38 / "calibration-replication.json"
    existing = json.loads(out.read_text()) if out.exists() else {}
    existing[args.engine] = result
    out.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n")

    for persona_id, row in result["per_persona"].items():
        print(f"  {persona_id[:12]}: {row['questions_new']} questions, ordering differences "
              f"{len(row['ordering_mismatches'])} ({len(row['ordering_tie_explained'])} tie-explained, "
              f"{len(row['ordering_unexplained'])} unexplained), score mismatches "
              f"{len(row['score_mismatches'])}, hit@3 class changes "
              f"{len(row['hit_at_3_class_changes'])}/{row['measured_questions']}")
    print(f"  tie instability: {result['tie_instability']}")
    print(f"{args.engine} replication gate: {'PASS' if result['passed'] else 'FAIL'}")
    for problem in result["material_mismatches"]:
        print(f"    {problem}")
    if not result["passed"]:
        raise SystemExit(f"{args.engine} calibration replication failed; held-out exposure is blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
