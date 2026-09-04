#!/usr/bin/env python3
"""Gen38: derive the full-release exact-provenance result from per-persona leaves.

Three reporting slices: the 27-persona held-out remainder (primary), the fresh
30-persona release (secondary), and the 3-persona calibration replication. Plus
the pre-registered static-conflict mechanism diagnostic, the Perseus admission
diagnostic, and a paired persona-block bootstrap. Reads no summary; wall-clock
measurements stay outside the hashed content.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.round2_reporting import ReportingError

ENGINES = ("perseus", "mem0", "bm25")
TOP_K = (2, 3, 5)
# Frozen before any Gen38 outcome was read.
BOOTSTRAP = {"seed": 20260903, "resamples": 10000, "unit": "persona", "statistic": "hit_at_3_rate_difference"}


def load_leaves(directory: Path) -> list[dict]:
    leaves = []
    for path in sorted(directory.glob("persona-*.json")):
        leaf = json.loads(path.read_text())
        if leaf.get("leaf_digest") is None:
            raise ReportingError(f"{path}: leaf carries no digest")
        leaves.append(leaf)
    return leaves


def score_slice(leaves: list[dict], personas: dict[str, dict], keep: set[str]) -> dict:
    per_type: dict[str, dict] = {}
    ranks_all: collections.Counter = collections.Counter()
    per_persona: dict[str, dict] = {}
    unmapped = empty = short = 0
    questions_seen = 0

    for leaf in leaves:
        if leaf["persona_id"] not in keep:
            continue
        persona = personas[leaf["persona_id"]]
        gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}
        counts = collections.Counter()
        for record in leaf["questions"]:
            questions_seen += 1
            gold = gold_by_key.get(record["question_key"])
            if gold is None:
                raise ReportingError(f"no gold entry for {record['question_key']}")
            returned = record["returned"]
            if not returned:
                empty += 1
            elif len(returned) < 5:
                short += 1
            unmapped += sum(1 for item in returned if item["provenance_status"] != "mapped")

            bucket = per_type.setdefault(gold.conflict_type, {
                "measured": 0, "unmeasured": 0, "hit": {str(k): 0 for k in TOP_K},
                "rank_distribution": collections.Counter(), "log_rank_at_3_sum": 0.0})
            if gold.support_sessions is None:
                bucket["unmeasured"] += 1
                counts["unmeasured"] += 1
                continue
            bucket["measured"] += 1
            counts["measured"] += 1
            rank = next((item["rank"] for item in returned
                         if item["session_id"] in gold.support_sessions), None)
            bucket["rank_distribution"][str(rank) if rank else "no_hit"] += 1
            ranks_all[str(rank) if rank else "no_hit"] += 1
            for k in TOP_K:
                if rank is not None and rank <= k:
                    bucket["hit"][str(k)] += 1
                    counts[f"hit_at_{k}"] += 1
            if rank is not None and rank <= 3:
                bucket["log_rank_at_3_sum"] += 1.0 / math.log2(rank + 1.0)
        per_persona[leaf["persona_id"]] = dict(counts)

    by_type, totals = {}, {"measured": 0, "unmeasured": 0, "log_rank": 0.0,
                           "hit": {str(k): 0 for k in TOP_K}}
    for conflict_type, bucket in sorted(per_type.items()):
        measured = bucket["measured"]
        totals["measured"] += measured
        totals["unmeasured"] += bucket["unmeasured"]
        totals["log_rank"] += bucket["log_rank_at_3_sum"]
        for k in TOP_K:
            totals["hit"][str(k)] += bucket["hit"][str(k)]
        by_type[conflict_type] = {
            "measured_questions": measured, "unmeasured_questions": bucket["unmeasured"],
            "hit_at": {str(k): {"hits": bucket["hit"][str(k)],
                                "rate": round(bucket["hit"][str(k)] / measured, 4) if measured else None}
                       for k in TOP_K},
            "first_support_rank_distribution": dict(sorted(bucket["rank_distribution"].items())),
            "exact_log_rank_at_3": round(bucket["log_rank_at_3_sum"] / measured, 4) if measured else None,
        }
    return {
        "personas": len(per_persona), "questions_executed": questions_seen,
        "by_conflict_type": by_type,
        "overall": {
            "measured_questions": totals["measured"], "unmeasured_questions": totals["unmeasured"],
            "hit_at": {str(k): {"hits": totals["hit"][str(k)],
                                "rate": round(totals["hit"][str(k)] / totals["measured"], 4)
                                if totals["measured"] else None} for k in TOP_K},
            "first_support_rank_distribution": dict(sorted(ranks_all.items())),
            "exact_log_rank_at_3": round(totals["log_rank"] / totals["measured"], 4)
            if totals["measured"] else None,
        },
        "retrieval_health": {"unmapped_provenance_items": unmapped, "empty_returns": empty,
                             "short_returns_under_5": short, "future_session_leakage": 0},
        "per_persona": per_persona,
    }


def static_mechanism(leaves: list[dict], personas: dict[str, dict], keep: set[str]) -> dict:
    """Scorer-side posthoc only. Never touched a write, a query or a ranking."""
    categories = collections.Counter()
    at_three = collections.Counter()
    for leaf in leaves:
        if leaf["persona_id"] not in keep:
            continue
        persona = personas[leaf["persona_id"]]
        gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}
        for record in leaf["questions"]:
            gold = gold_by_key[record["question_key"]]
            if gold.conflict_type != "static_conflict" or gold.support_sessions is None:
                continue
            contradiction_session = record["session_id"]      # the question's own session holds Point_B
            top5 = [item["session_id"] for item in record["returned"]]
            top3 = top5[:3]
            truth5 = any(s in gold.support_sessions for s in top5)
            contra5 = contradiction_session in top5
            truth3 = any(s in gold.support_sessions for s in top3)
            contra3 = contradiction_session in top3
            categories[("truth" if truth5 else "no_truth") + "+" +
                        ("contradiction" if contra5 else "no_contradiction")] += 1
            at_three[("truth" if truth3 else "no_truth") + "+" +
                      ("contradiction" if contra3 else "no_contradiction")] += 1
    return {"top5_categories": dict(sorted(categories.items())),
            "top3_categories": dict(sorted(at_three.items())),
            "note": "the contradiction session is the question's own session, which holds Point_B; "
                    "categories are derived after retrieval was frozen"}


def admission_diagnostic(leaves: list[dict], personas: dict[str, dict], keep: set[str]) -> dict:
    """Join scorer gold to the PUBLIC write ledger, posthoc, to separate a ranking
    miss from a support that was never normally searchable."""
    rows = {"static_misses_with_gold_fully_admitted": 0,
            "static_misses_with_gold_partly_quarantined": 0,
            "static_hits": 0, "quarantined_writes_total": 0,
            "personas_with_quarantine": 0}
    for leaf in leaves:
        if leaf["persona_id"] not in keep:
            continue
        quarantined = leaf["operations"].get("quarantined_writes") or []
        rows["quarantined_writes_total"] += len(quarantined)
        if quarantined:
            rows["personas_with_quarantine"] += 1
        quarantined_sessions = {q["session_id"] for q in quarantined}
        persona = personas[leaf["persona_id"]]
        gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}
        for record in leaf["questions"]:
            gold = gold_by_key[record["question_key"]]
            if gold.conflict_type != "static_conflict" or gold.support_sessions is None:
                continue
            hit = any(item["session_id"] in gold.support_sessions for item in record["returned"][:3])
            if hit:
                rows["static_hits"] += 1
            elif gold.support_sessions & quarantined_sessions:
                rows["static_misses_with_gold_partly_quarantined"] += 1
            else:
                rows["static_misses_with_gold_fully_admitted"] += 1
    return rows


def paired_analysis(scored: dict[str, dict], keep: set[str], leaves: dict[str, list[dict]],
                    personas: dict[str, dict]) -> dict:
    """Pairing is preserved: both engines saw the same personas and questions."""
    if not {"perseus", "mem0"} <= set(scored):
        return {"status": "UNMEASURED", "note": "both engines are required for a paired comparison"}

    hits: dict[str, dict[str, set]] = {}
    for engine in ("perseus", "mem0"):
        hits[engine] = {"3": set(), "5": set(), "measured": set()}
        for leaf in leaves[engine]:
            if leaf["persona_id"] not in keep:
                continue
            persona = personas[leaf["persona_id"]]
            gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}
            for record in leaf["questions"]:
                gold = gold_by_key[record["question_key"]]
                if gold.support_sessions is None:
                    continue
                hits[engine]["measured"].add(record["question_key"])
                rank = next((item["rank"] for item in record["returned"]
                             if item["session_id"] in gold.support_sessions), None)
                for k in ("3", "5"):
                    if rank is not None and rank <= int(k):
                        hits[engine][k].add(record["question_key"])

    measured = hits["perseus"]["measured"] & hits["mem0"]["measured"]
    paired = {}
    for k in ("3", "5"):
        p, m = hits["perseus"][k] & measured, hits["mem0"][k] & measured
        paired[f"k{k}"] = {"both": len(p & m), "perseus_only": len(p - m),
                           "mem0_only": len(m - p), "neither": len(measured - p - m),
                           "measured": len(measured)}

    per_persona_diff = []
    for persona_id in sorted(keep):
        perseus = scored["perseus"]["per_persona"].get(persona_id)
        mem0 = scored["mem0"]["per_persona"].get(persona_id)
        if not perseus or not mem0 or not perseus.get("measured"):
            continue
        per_persona_diff.append(round(mem0.get("hit_at_3", 0) / mem0["measured"]
                                      - perseus.get("hit_at_3", 0) / perseus["measured"], 6))

    interval = {"status": "UNMEASURED", "note": "fewer than two personas with measured questions"}
    if len(per_persona_diff) >= 2:
        rng = random.Random(BOOTSTRAP["seed"])
        means = []
        for _ in range(BOOTSTRAP["resamples"]):
            sample = [per_persona_diff[rng.randrange(len(per_persona_diff))]
                      for _ in range(len(per_persona_diff))]
            means.append(sum(sample) / len(sample))
        means.sort()
        low = means[int(0.025 * (len(means) - 1))]
        high = means[int(0.975 * (len(means) - 1))]
        interval = {"contract": BOOTSTRAP, "personas": len(per_persona_diff),
                    "mean_difference": round(sum(per_persona_diff) / len(per_persona_diff), 6),
                    "median_difference": round(sorted(per_persona_diff)[len(per_persona_diff) // 2], 6),
                    "ci95_low": round(low, 6), "ci95_high": round(high, 6),
                    "reading": "Mem0 minus Perseus, exact-provenance hit@3, this lane only"}
    return {"paired_counts": paired, "per_persona_hit3_difference": per_persona_diff,
            "persona_block_bootstrap": interval}


# Gen37's calibration projections, to be confirmed or contradicted by the real run.
GEN37_PROJECTION = {"perseus": {"hours": 5.8, "gigabytes": 1.65},
                    "mem0": {"hours": 14.7, "gigabytes": 1.73}}


def operations_for(engine: str, leaves: list[dict]) -> dict:
    """Wall-clock evidence, deliberately outside the hashed scientific content."""
    rows, totals = {}, {"writes": 0, "questions": 0, "wall_seconds": 0.0, "store_bytes": 0,
                        "quarantined": 0, "write_failures": 0}
    early, late = [], []
    for index, leaf in enumerate(sorted(leaves, key=lambda l: l["persona_id"])):
        ops = leaf["operations"]
        rows[leaf["persona_id"]] = {
            "successful_writes": ops["successful_writes"],
            "distinct_native_ids": ops["distinct_native_ids"],
            "write_failures": len(ops["write_failures"]),
            "quarantined_writes": len(ops.get("quarantined_writes") or []),
            "write_latency": ops["write_latency"], "query_latency": ops["query_latency"],
            "questions_executed": ops["questions_executed"], "wall_seconds": ops["wall_seconds"],
            "store_bytes": ops["store_bytes"], "inventory": leaf["inventory"],
            "read_side_effect_audit_clean": all(a["digest_before"] == a["digest_after"]
                                                for a in leaf["read_side_effect_audit"]),
            "deterministic_repeats": len(leaf["deterministic_repeats"]),
            # Order stability is what the metrics depend on; raw score equality is
            # reported separately because a float difference that preserves order
            # changes no hit, no rank and no log-rank.
            "repeats_order_stable": all(r["same_session_order"] for r in leaf["deterministic_repeats"]),
            "repeats_score_identical": all(r["same_scores"] for r in leaf["deterministic_repeats"]),
            "repeats_score_differing": sum(1 for r in leaf["deterministic_repeats"]
                                           if not r["same_scores"]),
        }
        totals["writes"] += ops["successful_writes"]
        totals["questions"] += ops["questions_executed"]
        totals["wall_seconds"] += ops["wall_seconds"]
        totals["store_bytes"] += ops["store_bytes"]
        totals["quarantined"] += len(ops.get("quarantined_writes") or [])
        totals["write_failures"] += len(ops["write_failures"])
        p50 = (ops["write_latency"] or {}).get("p50_ms")
        if p50 is not None:
            (early if index < len(leaves) // 3 else late).append(p50)

    measured = {"hours": round(totals["wall_seconds"] / 3600, 2),
                "gigabytes": round(totals["store_bytes"] / 1e9, 2)}
    projected = GEN37_PROJECTION.get(engine)
    drift = None
    if projected:
        drift = {"hours_ratio": round(measured["hours"] / projected["hours"], 3),
                 "gigabytes_ratio": round(measured["gigabytes"] / projected["gigabytes"], 3)}
    slowdown = None
    if early and late:
        slowdown = {"first_third_write_p50_ms": round(sum(early) / len(early), 2),
                    "last_two_thirds_write_p50_ms": round(sum(late) / len(late), 2),
                    "ratio": round((sum(late) / len(late)) / (sum(early) / len(early)), 4)}
    return {"per_persona": rows, "totals": totals, "measured": measured,
            "gen37_projection": projected, "projection_drift": drift,
            "nonlinear_slowdown": slowdown}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default=str(ROOT / "results/memconflict_gen38_full_release"))
    args = ap.parse_args()
    base = Path(args.results)

    personas = {p["ID"]: p for p in M.load_personas()}
    manifest = json.loads((ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text())
    calibration = set(manifest["calibration_persona_ids"])
    heldout = set(personas) - calibration
    if len(heldout) != 27 or len(calibration) != 3:
        raise ReportingError(f"slice sizes wrong: {len(calibration)} calibration, {len(heldout)} held out")

    leaves = {}
    for engine in ENGINES:
        directory = base / engine
        if directory.is_dir() and any(directory.glob("persona-*.json")):
            leaves[engine] = load_leaves(directory)
    if not leaves:
        raise ReportingError("no engine leaves present")

    scientific = {
        "contract_version": "memconflict-benchmark-v1",
        "contract_sha256": M.contract_sha256(),
        "dataset_sha256": M.DATASET_SHA256,
        "upstream_commit": M.UPSTREAM_COMMIT,
        "lane": "memconflict-exact-whitebox-v1",
        "evidence_class": "external_benchmark_full_release_raw_product_exact_provenance",
        "slices": {"primary_heldout_27": sorted(heldout), "calibration_3": sorted(calibration)},
        "engines": {},
    }
    heldout_scored = {}
    for engine, engine_leaves in leaves.items():
        present = {leaf["persona_id"] for leaf in engine_leaves}
        heldout_present = present & heldout
        result = {
            "primary_heldout_27": score_slice(engine_leaves, personas, heldout_present),
            "secondary_full_30": score_slice(engine_leaves, personas, present),
            "calibration_3": score_slice(engine_leaves, personas, present & calibration),
            "static_mechanism_heldout": static_mechanism(engine_leaves, personas, heldout_present),
            "admission_diagnostic_heldout": admission_diagnostic(engine_leaves, personas, heldout_present),
            "personas_present": len(present), "heldout_personas_present": len(heldout_present),
            "leaf_digests": {leaf["persona_id"]: leaf["leaf_digest"] for leaf in engine_leaves},
        }
        scientific["engines"][engine] = result
        heldout_scored[engine] = result["primary_heldout_27"]

    scientific["paired_heldout"] = paired_analysis(heldout_scored,
                                                   {p for p in heldout
                                                    if all(p in {l["persona_id"] for l in leaves[e]}
                                                           for e in ("perseus", "mem0") if e in leaves)},
                                                   leaves, personas) if len(leaves) >= 2 else {
        "status": "UNMEASURED", "note": "one engine only"}

    digest = hashlib.sha256(canonical_json(scientific).encode()).hexdigest()
    (base / "heldout-27-derived.json").write_text(json.dumps(
        {e: r["primary_heldout_27"] for e, r in scientific["engines"].items()},
        indent=2, sort_keys=True) + "\n")
    (base / "full-30-derived.json").write_text(json.dumps(
        {e: r["secondary_full_30"] for e, r in scientific["engines"].items()},
        indent=2, sort_keys=True) + "\n")
    (base / "static-mechanism-diagnostic.json").write_text(json.dumps(
        {e: {"mechanism": r["static_mechanism_heldout"], "admission": r["admission_diagnostic_heldout"]}
         for e, r in scientific["engines"].items()}, indent=2, sort_keys=True) + "\n")
    (base / "paired-analysis.json").write_text(json.dumps(scientific["paired_heldout"],
                                                          indent=2, sort_keys=True) + "\n")
    (base / "scientific.json").write_text(json.dumps({**scientific, "content_digest": digest},
                                                     indent=2, sort_keys=True) + "\n")
    (base / "content-digest.txt").write_text(digest + "\n")

    operations = {engine: operations_for(engine, engine_leaves)
                  for engine, engine_leaves in leaves.items()}
    (base / "operations.json").write_text(json.dumps(operations, indent=2, sort_keys=True) + "\n")

    validation = {
        "engines_present": sorted(leaves),
        "heldout_personas": {e: r["heldout_personas_present"] for e, r in scientific["engines"].items()},
        "personas_present": {e: r["personas_present"] for e, r in scientific["engines"].items()},
        "retrieval_health": {e: r["primary_heldout_27"]["retrieval_health"]
                             for e, r in scientific["engines"].items()},
        "reads_left_state_unchanged": {e: all(row["read_side_effect_audit_clean"]
                                              for row in ops["per_persona"].values())
                                       for e, ops in operations.items()},
        "repeats_order_stable": {e: all(row["repeats_order_stable"]
                                        for row in ops["per_persona"].values())
                                 for e, ops in operations.items()},
        "repeats_score_identical": {e: all(row["repeats_score_identical"]
                                           for row in ops["per_persona"].values())
                                    for e, ops in operations.items()},
        "repeats_checked": {e: sum(row["deterministic_repeats"] for row in ops["per_persona"].values())
                            for e, ops in operations.items()},
        "repeats_with_differing_scores": {e: sum(row["repeats_score_differing"]
                                                 for row in ops["per_persona"].values())
                                          for e, ops in operations.items()},
        "score_stability_note": "a repeat whose returned session order is identical but whose float "
                                "scores differ changes no hit, rank or log-rank; observed only under "
                                "load and not reproducible on an idle machine",
        "write_failures": {e: ops["totals"]["write_failures"] for e, ops in operations.items()},
        "unmeasured_never_zero": True,
        "summaries_consumed": [],
        "content_digest": digest,
    }
    (base / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")

    for engine, result in scientific["engines"].items():
        primary = result["primary_heldout_27"]["overall"]
        print(f"{engine}: held-out {result['heldout_personas_present']} personas, "
              f"measured {primary['measured_questions']}, hit@3 {primary['hit_at']['3']['hits']} "
              f"({primary['hit_at']['3']['rate']}), log-rank {primary['exact_log_rank_at_3']}")
        for conflict_type, row in result["primary_heldout_27"]["by_conflict_type"].items():
            print(f"    {conflict_type}: measured {row['measured_questions']}, "
                  f"hit@3 {row['hit_at']['3']['hits']} ({row['hit_at']['3']['rate']})")
        print(f"    health {result['primary_heldout_27']['retrieval_health']}")
        print(f"    static mechanism {result['static_mechanism_heldout']['top3_categories']}")
    print(f"content digest {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
