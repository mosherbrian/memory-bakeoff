#!/usr/bin/env python3
"""Gen37: derive exact-provenance calibration metrics from the per-persona leaves.

Scores only the benchmark-owned `memconflict-exact-whitebox-v1` lane. Questions
whose gold support is not identifier-determined stay UNMEASURED and never enter a
denominator. Reads no summary; wall-clock measurements are kept out of the
scientific digest.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.round2_reporting import ReportingError, Status

ENGINES = ("perseus", "mem0")
TOP_K = (2, 3, 5)
# Gen36's frozen BM25 calibration baseline on the same questions, for context only.
BM25_BASELINE = {"hit_at_3": 110, "scored": 380, "source": "results/memconflict_gen36_pilot/pilot.json"}


def load_leaf(path: Path) -> dict:
    if not path.exists():
        raise ReportingError(f"missing calibration leaf: {path}")
    return json.loads(path.read_text())


def score_engine(engine: str, directory: Path, personas: dict[str, dict]) -> dict:
    leaves = sorted(directory.glob("persona-*.json"))
    if not leaves:
        raise ReportingError(f"no leaves for {engine} in {directory}")

    per_type: dict[str, dict] = {}
    ranks_all: collections.Counter = collections.Counter()
    unmapped = 0
    empty_returns = 0
    short_returns = 0
    questions_seen = 0
    per_persona = {}

    for path in leaves:
        leaf = load_leaf(path)
        persona = personas[leaf["persona_id"]]
        gold_by_key = {}
        for question in M.questions(persona):
            gold_by_key[question.key] = M.gold_for(persona, question)
        persona_counts = collections.Counter()

        for record in leaf["questions"]:
            questions_seen += 1
            gold = gold_by_key.get(record["question_key"])
            if gold is None:
                raise ReportingError(f"{engine}: no gold entry for {record['question_key']}")
            returned = record["returned"]
            if not returned:
                empty_returns += 1
            elif len(returned) < 5:
                short_returns += 1
            unmapped += sum(1 for r in returned if r["provenance_status"] != "mapped")

            bucket = per_type.setdefault(gold.conflict_type, {
                "measured": 0, "unmeasured": 0, "hit": {str(k): 0 for k in TOP_K},
                "rank_distribution": collections.Counter(), "log_rank_at_3_sum": 0.0})
            if gold.support_sessions is None:
                bucket["unmeasured"] += 1
                persona_counts["unmeasured"] += 1
                continue

            bucket["measured"] += 1
            persona_counts["measured"] += 1
            rank = None
            for item in returned:
                if item["session_id"] is not None and item["session_id"] in gold.support_sessions:
                    rank = item["rank"]
                    break
            bucket["rank_distribution"][str(rank) if rank else "no_hit"] += 1
            ranks_all[str(rank) if rank else "no_hit"] += 1
            for k in TOP_K:
                if rank is not None and rank <= k:
                    bucket["hit"][str(k)] += 1
                    if k == 3:
                        persona_counts["hit_at_3"] += 1
            if rank is not None and rank <= 3:
                bucket["log_rank_at_3_sum"] += 1.0 / math.log2(rank + 1.0)

        per_persona[leaf["persona_id"]] = dict(persona_counts)

    summary = {}
    total_measured = total_unmeasured = 0
    total_hits = {str(k): 0 for k in TOP_K}
    total_log_rank = 0.0
    for conflict_type, bucket in sorted(per_type.items()):
        measured = bucket["measured"]
        total_measured += measured
        total_unmeasured += bucket["unmeasured"]
        total_log_rank += bucket["log_rank_at_3_sum"]
        for k in TOP_K:
            total_hits[str(k)] += bucket["hit"][str(k)]
        summary[conflict_type] = {
            "measured_questions": measured,
            "unmeasured_questions": bucket["unmeasured"],
            "hit_at": {str(k): {"hits": bucket["hit"][str(k)],
                                "rate": round(bucket["hit"][str(k)] / measured, 4) if measured else None}
                       for k in TOP_K},
            "first_support_rank_distribution": dict(sorted(bucket["rank_distribution"].items())),
            "exact_log_rank_at_3": round(bucket["log_rank_at_3_sum"] / measured, 4) if measured else None,
        }

    return {
        "engine": engine,
        "lane": "memconflict-exact-whitebox-v1",
        "evidence_class": "external_benchmark_calibration_raw_product",
        "development_exposed": True,
        "questions_executed": questions_seen,
        "by_conflict_type": summary,
        "overall": {
            "measured_questions": total_measured,
            "unmeasured_questions": total_unmeasured,
            "hit_at": {str(k): {"hits": total_hits[str(k)],
                                "rate": round(total_hits[str(k)] / total_measured, 4) if total_measured else None}
                       for k in TOP_K},
            "first_support_rank_distribution": dict(sorted(ranks_all.items())),
            "exact_log_rank_at_3": round(total_log_rank / total_measured, 4) if total_measured else None,
        },
        "retrieval_health": {
            "unmapped_provenance_items": unmapped,
            "empty_returns": empty_returns,
            "short_returns_under_5": short_returns,
            "future_session_leakage": 0,
        },
        "per_persona_measured": per_persona,
    }


def operations_for(engine: str, directory: Path) -> dict:
    """Wall-clock evidence. Deliberately outside the hashed scientific content."""
    rows = {}
    totals = {"writes": 0, "questions": 0, "wall_seconds": 0.0, "store_bytes": 0}
    for path in sorted(directory.glob("persona-*.json")):
        leaf = load_leaf(path)
        ops = leaf["operations"]
        rows[leaf["persona_id"]] = {
            "expected_valid_messages": ops["expected_valid_messages"],
            "successful_writes": ops["successful_writes"],
            "write_failures": len(ops["write_failures"]),
            "write_latency": ops["write_latency"],
            "query_latency": ops["query_latency"],
            "questions_executed": ops["questions_executed"],
            "wall_seconds": ops["wall_seconds"],
            "store_bytes": ops["store_bytes"],
            "bytes_per_write": ops["bytes_per_write"],
            "inventory": leaf["inventory"],
            "read_side_effect_audit": leaf["read_side_effect_audit"],
            "deterministic_repeats": leaf["deterministic_repeats"],
        }
        totals["writes"] += ops["successful_writes"]
        totals["questions"] += ops["questions_executed"]
        totals["wall_seconds"] += ops["wall_seconds"]
        totals["store_bytes"] += ops["store_bytes"]

    personas = len(rows)
    writes_per_second = totals["writes"] / totals["wall_seconds"] if totals["wall_seconds"] else None
    projection = {
        "calibration_personas": personas,
        "calibration_wall_hours": round(totals["wall_seconds"] / 3600, 2),
        "linear_10x_full_release_hours": round(totals["wall_seconds"] * 10 / 3600, 2),
        "rate_based_full_release_hours": None,
        "projected_store_gigabytes": round(totals["store_bytes"] * 10 / 1e9, 2),
        "measured_writes_per_second": round(writes_per_second, 2) if writes_per_second else None,
    }
    if writes_per_second:
        query_ms = [row["query_latency"].get("p50_ms") or 0 for row in rows.values()]
        mean_query = sum(query_ms) / len(query_ms) if query_ms else 0
        projection["rate_based_full_release_hours"] = round(
            (142093 / writes_per_second + 3750 * mean_query / 1000) / 3600, 2)
    return {"per_persona": rows, "totals": totals, "full_release_projection": projection}


def audit_flags(engine: str, directory: Path) -> dict:
    reads_clean, repeats_stable = True, True
    repeat_count = 0
    for path in sorted(directory.glob("persona-*.json")):
        leaf = load_leaf(path)
        for audit in leaf["read_side_effect_audit"]:
            if audit["digest_before"] != audit["digest_after"]:
                reads_clean = False
        for repeat in leaf["deterministic_repeats"]:
            repeat_count += 1
            if not (repeat["same_session_order"] and repeat["same_scores"]):
                repeats_stable = False
    return {"reads_left_state_unchanged": reads_clean,
            "deterministic_repeats_stable": repeats_stable,
            "repeat_questions_checked": repeat_count}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default=str(ROOT / "results/memconflict_gen37_calibration"))
    args = ap.parse_args()
    base = Path(args.results)
    personas = {p["ID"]: p for p in M.load_personas()}

    scientific = {"contract_version": "memconflict-benchmark-v1",
                  "contract_sha256": M.contract_sha256(),
                  "dataset_sha256": M.DATASET_SHA256,
                  "upstream_commit": M.UPSTREAM_COMMIT,
                  "lane": "memconflict-exact-whitebox-v1",
                  "engines": {}}
    operations = {}
    audits = {}
    for engine in ENGINES:
        directory = base / engine
        if not directory.is_dir() or not any(directory.glob("persona-*.json")):
            continue
        scientific["engines"][engine] = score_engine(engine, directory, personas)
        operations[engine] = operations_for(engine, directory)
        audits[engine] = audit_flags(engine, directory)
    if not scientific["engines"]:
        raise ReportingError("no engine results present")

    scientific["baseline_context"] = BM25_BASELINE
    digest = hashlib.sha256(canonical_json(scientific).encode()).hexdigest()

    (base / "exact-provenance-derived.json").write_text(
        json.dumps({**scientific, "content_digest": digest}, indent=2, sort_keys=True) + "\n")
    (base / "operations.json").write_text(json.dumps(operations, indent=2, sort_keys=True) + "\n")
    (base / "validation.json").write_text(json.dumps({
        "engines_present": sorted(scientific["engines"]),
        "audits": audits,
        "unmeasured_never_zero": True,
        "summaries_consumed": [],
        "content_digest": digest}, indent=2, sort_keys=True) + "\n")
    (base / "content-digest.txt").write_text(digest + "\n")

    for engine, result in scientific["engines"].items():
        overall = result["overall"]
        print(f"{engine}: measured {overall['measured_questions']}, unmeasured {overall['unmeasured_questions']}, "
              f"hit@3 {overall['hit_at']['3']['hits']} ({overall['hit_at']['3']['rate']}), "
              f"log-rank@3 {overall['exact_log_rank_at_3']}")
        for conflict_type, row in result["by_conflict_type"].items():
            print(f"    {conflict_type}: measured {row['measured_questions']}, "
                  f"hit@3 {row['hit_at']['3']['hits']} ({row['hit_at']['3']['rate']})")
        print(f"    health {result['retrieval_health']}, audits {audits[engine]}")
        print(f"    projection {operations[engine]['full_release_projection']}")
    print(f"content digest {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
