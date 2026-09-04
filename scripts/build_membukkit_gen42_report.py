#!/usr/bin/env python3
"""Build the Gen42 MemBukkit calibration report from the committed leaves.

Scoring reuses the frozen Gen37 scorer and the Gen38 static-mechanism
diagnostic unchanged, so these numbers are comparable with the committed
calibration results by construction rather than by resemblance.
"""
from __future__ import annotations

import collections, hashlib, importlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import memconflict as M  # noqa: E402
from memory_bakeoff.round2_reporting import ReportingError  # noqa: E402

G37R = importlib.import_module("build_memconflict_gen37_report")
G38R = importlib.import_module("build_memconflict_gen38_report")

BASE = ROOT / "results" / "membukkit_memconflict_gen42_calibration"
VOLATILE = {"wall_seconds", "write_latency", "query_latency", "latency_ms",
            "mean_latency_ms", "generated_at", "operations"}


def leaves() -> list[dict]:
    found = sorted(BASE.glob("persona-*.json"))
    if not found:
        raise ReportingError(f"no Gen42 leaves in {BASE}")
    return [json.loads(p.read_text()) for p in found]


def ledger_for(persona_id: str) -> dict:
    return json.loads((BASE / f"ledger-{persona_id}.json").read_text())


def routing_diagnostic(all_leaves: list[dict], personas: dict[str, dict]) -> dict:
    """Split static misses into routing exclusion and rank loss.

    Scorer-side and posthoc: the opened candidate region was recorded while the
    query ran, and gold is joined to it only here, after retrieval was frozen.
    """
    rows = collections.Counter()
    gold_written = collections.Counter()
    per_persona: dict[str, dict] = {}
    for leaf in all_leaves:
        persona = personas[leaf["persona_id"]]
        ledger = ledger_for(leaf["persona_id"])
        sessions_by_id: dict[str, set[str]] = collections.defaultdict(set)
        for native_id, entry in ledger.items():
            sessions_by_id[entry["session_id"]].add(native_id)
        gold_by_key = {q.key: M.gold_for(persona, q) for q in M.questions(persona)}
        region_by_key = {r["question_key"]: set(r["candidate_region_native_ids"])
                         for r in leaf["routing"]}
        counts = collections.Counter()

        for record in leaf["questions"]:
            gold = gold_by_key[record["question_key"]]
            if gold.conflict_type != "static_conflict" or gold.support_sessions is None:
                continue
            gold_ids: set[str] = set()
            for session_id in gold.support_sessions:
                gold_ids |= sessions_by_id.get(session_id, set())
            if not gold_ids:
                gold_written["gold_support_not_found_in_write_ledger"] += 1
                counts["gold_support_missing_from_store"] += 1
                continue
            gold_written["gold_support_present_in_write_ledger"] += 1

            hit = any(item["session_id"] in gold.support_sessions for item in record["returned"])
            if hit:
                rows["static_hit_at_5"] += 1
                counts["hit"] += 1
                continue
            region = region_by_key.get(record["question_key"], set())
            if gold_ids & region:
                rows["miss_gold_entered_region_lost_before_top5"] += 1
                counts["miss_rank_loss"] += 1
            else:
                rows["miss_gold_never_entered_region"] += 1
                counts["miss_routing_exclusion"] += 1
        per_persona[leaf["persona_id"]] = dict(counts)

    misses = rows["miss_gold_never_entered_region"] + rows["miss_gold_entered_region_lost_before_top5"]
    return {
        "counts": dict(sorted(rows.items())),
        "gold_availability": dict(sorted(gold_written.items())),
        "per_persona": per_persona,
        "share_of_static_misses": {
            "routing_exclusion": round(rows["miss_gold_never_entered_region"] / misses, 4) if misses else None,
            "rank_loss": round(rows["miss_gold_entered_region_lost_before_top5"] / misses, 4) if misses else None,
        },
        "note": (
            "A = the gold support record was never inside the opened candidate region; "
            "B = it entered the region and did not survive to the native top five. "
            "The direct raw path has no admission or quarantine step, so an A is routing "
            "unreachability, not an availability event"
        ),
    }


def determinism(all_leaves: list[dict]) -> dict:
    repeats = [r for leaf in all_leaves for r in leaf["deterministic_repeats"]]
    return {
        "repeat_probes": len(repeats),
        "returned_order_identical": sum(1 for r in repeats if r["same_session_order"]),
        "numeric_scores_identical": sum(1 for r in repeats if r["same_scores"]),
        "selected_set_identical": sum(1 for r in repeats if r["same_session_order"]),
        "note": (
            "order and score identity are counted separately; selected-set identity is "
            "implied by order identity here because every probe that matched in order "
            "matched item for item"
        ),
    }


def operations(all_leaves: list[dict]) -> dict:
    total = collections.Counter()
    scans: list[float] = []
    per_persona = {}
    for leaf in all_leaves:
        ops = leaf["operations"]
        for key in ("attempted_writes", "successful_writes", "distinct_native_ids",
                    "malformed_excluded", "questions_executed", "duplicate_message_texts"):
            total[key] += ops[key]
        total["write_failures"] += len(ops["write_failures"])
        total["native_id_replacements"] += len(ops["native_id_replacements"])
        for row in leaf["routing"]:
            trace = row.get("trace") or {}
            if trace.get("n_facts"):
                scans.append(trace["n_scanned"] / trace["n_facts"])
        per_persona[leaf["persona_id"]] = {
            "writes": ops["successful_writes"],
            "questions": ops["questions_executed"],
            "wall_seconds": ops["wall_seconds"],
            "write_p50_ms": ops["write_latency"].get("p50_ms"),
            "query_p50_ms": ops["query_latency"].get("p50_ms"),
            "store_bytes": ops["store_bytes"],
            "inventory": leaf["inventory"],
        }
    scans.sort()

    def pct(p: float):
        return round(scans[min(len(scans) - 1, int(p * len(scans)))], 4) if scans else None

    return {
        "totals": dict(sorted(total.items())),
        "per_persona": per_persona,
        "scan_fraction": {"n": len(scans), "p50": pct(0.5), "p90": pct(0.9), "max": pct(0.999),
                          "derived_from": "native trace n_scanned / n_facts"},
    }


def context() -> dict:
    """Committed calibration numbers from earlier generations, read as published.

    Nothing here is recomputed: these are the Gen37 leaves as committed, so the
    comparison is against the record rather than a re-derivation of it.
    """
    source = ROOT / "results" / "memconflict_gen37_calibration" / "exact-provenance-derived.json"
    if not source.exists():
        return {"status": "UNMEASURED", "reason": f"{source} not present"}
    payload = json.loads(source.read_text())
    out: dict = {"source": str(source.relative_to(ROOT)),
                 "baseline_context": payload.get("baseline_context")}
    for engine, block in (payload.get("engines") or {}).items():
        overall = block.get("overall") or {}
        out[engine] = {
            "hit_at_3": (overall.get("hit_at") or {}).get("3", {}).get("rate"),
            "measured_questions": overall.get("measured_questions"),
            "exact_log_rank_at_3": overall.get("exact_log_rank_at_3"),
            "by_conflict_type_hit_at_3": {
                t: (b.get("hit_at") or {}).get("3", {}).get("rate")
                for t, b in (block.get("by_conflict_type") or {}).items()
            },
        }
    return out


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in sorted(obj.items()) if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main() -> int:
    personas = {p["ID"]: p for p in M.load_personas()}
    all_leaves = leaves()
    scored = G37R.score_engine("membukkit", BASE, personas)
    scored["evidence_class"] = "external_benchmark_calibration_raw_product_exact_provenance"
    keep = {leaf["persona_id"] for leaf in all_leaves}

    payload = {
        "identity": json.loads((BASE / "identity.json").read_text()),
        "scored": scored,
        "static_mechanism": G38R.static_mechanism(all_leaves, personas, keep),
        "routing_diagnostic": routing_diagnostic(all_leaves, personas),
        "determinism": determinism(all_leaves),
        "operations": operations(all_leaves),
        "committed_calibration_context": context(),
    }
    payload["scientific_digest"] = hashlib.sha256(
        json.dumps(strip(payload), sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()

    (BASE / "calibration-report.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({
        "overall_hit_at_3": scored["overall"]["hit_at"]["3"],
        "measured": scored["overall"]["measured_questions"],
        "unmeasured": scored["overall"]["unmeasured_questions"],
        "by_type": {t: b["hit_at"]["3"] for t, b in scored["by_conflict_type"].items()},
        "retrieval_health": scored["retrieval_health"],
        "routing": payload["routing_diagnostic"]["counts"],
        "digest": payload["scientific_digest"][:16],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
