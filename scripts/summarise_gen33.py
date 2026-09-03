#!/usr/bin/env python3
"""Aggregate Gen33 and build the four-engine architectural contrast."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import agentmemory_longitudinal as A

OUT = ROOT / "results/agentmemory_gen33_longitudinal"
PREFLIGHT = ROOT / ".control-plane/gen33-preflight.json"
PRIOR = {"gen29_perseus": "results/perseus_vault_gen29_longitudinal/summary.json",
         "gen31_hindsight": "results/hindsight_gen31_longitudinal/summary.json",
         "gen32_mem0": "results/mem0_gen32_longitudinal/summary.json"}
SHARED_SEVEN = ("stale_persistence", "configuration_collapse", "failed_procedure_adoption",
                "late_history_corruption", "false_persistence", "missing_required_truth", "unsupported_evidence")

reps = [json.loads(p.read_text()) for p in sorted(OUT.glob("repetition-*.json"))]
if len(reps) != 3:
    raise SystemExit(f"expected 3 repetitions, found {len(reps)}")

totals: dict[str, int] = {}
for rep in reps:
    for name, count in rep["failure_totals"].items():
        totals[name] = totals.get(name, 0) + count
nonzero = {k: v for k, v in sorted(totals.items()) if v}

prior = {}
for label, rel in PRIOR.items():
    path = ROOT / rel
    if path.exists():
        prior[label] = {k: v for k, v in json.loads(path.read_text()).get("failure_totals_all_repetitions", {}).items() if v}

append_only = [prior[k] for k in ("gen29_perseus", "gen31_hindsight", "gen32_mem0") if k in prior]
identical_across_append_only = sorted(
    c for c in SHARED_SEVEN
    if append_only and len({p.get(c, 0) for p in append_only}) == 1 and append_only[0].get(c, 0)) if append_only else []

events = reps[0]["supersession_events"]
preflight = json.loads(PREFLIGHT.read_text()) if PREFLIGHT.exists() else {}

lifecycle_totals: dict[str, int] = {}
for rep in reps:
    for name, count in rep.get("lifecycle_failure_totals", {}).items():
        lifecycle_totals[name] = lifecycle_totals.get(name, 0) + count

summary = {
    "generation": 33,
    "status": "complete_raw_product_longitudinal_native_retirement_activated",
    "evidence_class": "raw_product",
    "fixture_version": L.FIXTURE_VERSION, "fixture_sha256": L.fixture_sha256(),
    "scorer_version": L.SCORER_VERSION, "scorer_contract_sha256": L.scorer_contract_sha256(),
    "adapter_version": A.ADAPTER_VERSION, "adapter_contract_sha256": A.adapter_contract_sha256(),
    "adapter_contract": A.adapter_contract_payload(),
    "system_identity": {
        "product": "agentmemory", "product_version": "0.9.29",
        "upstream_commit": "e04ba88819c365c9acf9d6661ea802143e728bd6",
        "endpoints": "/agentmemory/remember + /agentmemory/smart-search",
        "embeddings": "local q8 Xenova/all-MiniLM-L6-v2, 384-D, @huggingface/transformers 4.2.0",
        "retrieval": "native in-memory cosine + BM25 RRF k=60, vector 0.6 / BM25 0.4, 5% stream-agreement bonus, <=3 per session",
        "isolation": "fresh iii data directory and distinct agentId per repetition; one project namespace",
        "disabled": ["LLM provider/extractor", "CONSOLIDATION_ENABLED", "GRAPH_EXTRACTION_ENABLED",
                     "AGENTMEMORY_AUTO_COMPRESS", "learned reranking"],
        "requested_limit": 5, "reader": "none", "inference_server": "none",
    },
    "model_or_product_llm_calls": False,
    "treatment_activation": {
        "question": "does native write-time supersession fire on longitudinal-v1 at all?",
        "activated": all(r["supersession_count"] > 0 for r in reps),
        "supersessions_per_repetition": [r["supersession_count"] for r in reps],
        "classification_is_harness_judgement_of_product_retirements_not_a_scorer_output": True,
        "classification_per_repetition": [r["supersession_classification"] for r in reps],
        "events_repetition_1": [{"at_ingestion_order": e["at_ingestion_order"],
                                 "predecessor_canonical_id": e["predecessor_canonical_id"],
                                 "successor_canonical_id": e["successor_canonical_id"],
                                 "classification": e["classification"]} for e in events],
        "rule": A.adapter_contract_payload()["native_lifecycle_rule"],
        "why_it_fired": ("the tokenizer drops whitespace tokens of two characters or fewer, so C1/C2 and 21/29 "
                         "vanish and the surviving token sets are identical, scoring Jaccard 1.000"),
        "predicted_before_running": "L001/L003 and L002/L004 were the only fixture pairs above 0.7; both fired, as predicted",
        "preflight_validation": {"synthetic_pair_superseded": preflight.get("supersession_fired"),
                                 "retired_row_still_in_kv": preflight.get("superseded_still_in_kv"),
                                 "retired_row_absent_from_search": preflight.get("superseded_absent_from_search")},
    },
    "repetitions": [{"repetition": r["repetition"], "agent_id": r["agent_id"], "cases": len(r["cases"]),
                     "checkpoints": len(r["checkpoint_state"]),
                     "provenance_exact_all_cases": all(c["provenance_exact_all"] for c in r["cases"]),
                     "supersession_count": r["supersession_count"],
                     "supersession_classification": r["supersession_classification"],
                     "failure_totals": r["failure_totals"],
                     "lifecycle_failure_totals": r["lifecycle_failure_totals"],
                     "checkpoint_state": r["checkpoint_state"]} for r in reps],
    "repetition_variance": "none; all three repetitions produced identical failure totals and identical supersessions"
                            if all(r["failure_totals"] == reps[0]["failure_totals"] for r in reps) else "repetitions differ",
    "failure_totals_all_repetitions": nonzero,
    "lifecycle_failure_totals_all_repetitions": {k: v for k, v in sorted(lifecycle_totals.items()) if v},
    "scorer_streams": ("case failures come from score_longitudinal_case; lifecycle failures from score_lifecycle_state; they are separate scorer outputs and must never be merged or read for each other"),
    "four_engine_contrast": {
        "note": "capability surfaces only; not a numeric leaderboard",
        "append_only_gen29_perseus": prior.get("gen29_perseus", {}),
        "append_only_gen31_hindsight": prior.get("gen31_hindsight", {}),
        "append_only_gen32_mem0": prior.get("gen32_mem0", {}),
        "retiring_gen33_agentmemory": nonzero,
        "identical_across_all_three_append_only": identical_across_append_only,
        "per_class_delta_vs_each_append_only_engine": {
            klass: {"gen33_agentmemory": nonzero.get(klass, 0),
                    **{label: prior.get(label, {}).get(klass, 0) for label in PRIOR}}
            for klass in sorted(set(nonzero) | {k for p in append_only for k in p})
        },
        "reduced_versus_every_append_only_engine": sorted(
            c for c in SHARED_SEVEN
            if append_only and all(nonzero.get(c, 0) < p.get(c, 0) for p in append_only)),
        "reduced_versus_at_least_one": sorted(
            c for c in SHARED_SEVEN
            if append_only and any(nonzero.get(c, 0) < p.get(c, 0) for p in append_only)
            and not all(nonzero.get(c, 0) >= p.get(c, 0) for p in append_only)),
        "absent_from_every_append_only_engine": sorted(
            c for c in nonzero if not any(p.get(c, 0) for p in append_only)),
        "present_in_perseus_only_among_append_only": sorted(
            c for c in nonzero
            if prior.get("gen29_perseus", {}).get(c, 0)
            and not prior.get("gen31_hindsight", {}).get(c, 0)
            and not prior.get("gen32_mem0", {}).get(c, 0)),
    },
    "interpretation": ("Retirement is a real trade, not an improvement. Native supersession reduced most of the "
                       "append-only failure classes and introduced false supersession and history erasure in their "
                       "place, from the same blind lexical rule: an identical Jaccard score of 1.000 produced one "
                       "correct retirement and one wrong one. Neither architecture is safe; they fail differently. "
                       "This remains a two-arm architectural contrast across products, not a controlled experiment "
                       "within one product."),
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"wrote {OUT}/summary.json")
print(" variance:", summary["repetition_variance"])
print(" activated:", summary["treatment_activation"]["activated"],
      summary["treatment_activation"]["classification_per_repetition"][0])
c = summary["four_engine_contrast"]
print(" identical across append-only trio:", c["identical_across_all_three_append_only"])
print(" reduced vs EVERY append-only engine:", c["reduced_versus_every_append_only_engine"])
print(" reduced vs at least one:", c["reduced_versus_at_least_one"])
print(" absent from every append-only engine:", c["absent_from_every_append_only_engine"])
print(" present in Perseus only:", c["present_in_perseus_only_among_append_only"])
for k, v in c["per_class_delta_vs_each_append_only_engine"].items():
    print(f"   {k:26} am={v['gen33_agentmemory']:2}  P={v['gen29_perseus']:2}  H={v['gen31_hindsight']:2}  M={v['gen32_mem0']:2}")
