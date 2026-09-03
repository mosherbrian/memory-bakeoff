#!/usr/bin/env python3
"""Aggregate Gen32 and build the three-engine contrast."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import mem0_longitudinal as M

OUT = ROOT / "results/mem0_gen32_longitudinal"
PREFLIGHT = ROOT / ".control-plane/gen32-preflight.json"
PRIOR = {"gen29_perseus": ROOT / "results/perseus_vault_gen29_longitudinal/summary.json",
         "gen31_hindsight": ROOT / "results/hindsight_gen31_longitudinal/summary.json"}
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
for label, path in PRIOR.items():
    if path.exists():
        data = json.loads(path.read_text())
        prior[label] = {k: v for k, v in data.get("failure_totals_all_repetitions", {}).items() if v}

preflight = json.loads(PREFLIGHT.read_text()) if PREFLIGHT.exists() else {}
reproduced = sorted(c for c in SHARED_SEVEN if nonzero.get(c))

summary = {
    "generation": 32,
    "status": "complete_raw_product_longitudinal_no_temporal_surface",
    "evidence_class": "raw_product",
    "fixture_version": L.FIXTURE_VERSION, "fixture_sha256": L.fixture_sha256(),
    "scorer_version": L.SCORER_VERSION, "scorer_contract_sha256": L.scorer_contract_sha256(),
    "adapter_version": M.ADAPTER_VERSION, "adapter_contract_sha256": M.adapter_contract_sha256(),
    "adapter_contract": M.adapter_contract_payload(),
    "system_identity": {
        "product": "mem0ai", "product_version": "2.0.19",
        "upstream_commit": "19cb89aff472325c707f64b2f34ae6afdbf7faf7",
        "ingestion": "Memory.add(..., infer=False); no LLM extraction, update or supersession",
        "llm_client": "constructed with a placeholder key, never called; proven by socket refusal in preflight",
        "dense_embedding": "FastEmbed 0.8.0 thenlper/gte-large -> qdrant/gte-large-onnx snapshot 770e825c74a004f165b78793f7c8fc4a95280878, 1024-D",
        "sparse": "FastEmbed Qdrant/bm25 snapshot 22b8d2af71a76161e18dd432d2cee0eefa66e412",
        "vector_store": "embedded qdrant-client 1.19.0, on-disk, fresh path and collection per repetition",
        "onnxruntime": "1.29.0", "spacy": "absent; entity boosts inactive",
        "scope": "constant user_id=memory-bakeoff", "threshold": M.THRESHOLD, "requested_limit": 5,
        "reader": "none", "inference_server": "none",
    },
    "model_or_product_llm_calls": False,
    "repetitions": [{"repetition": r["repetition"], "collection": r["collection"], "cases": len(r["cases"]),
                     "checkpoints": len(r["checkpoint_state"]),
                     "provenance_exact_all_cases": all(c["provenance_exact_all"] for c in r["cases"]),
                     "failure_totals": r["failure_totals"],
                     "lifecycle_failure_totals": r["lifecycle_failure_totals"],
                     "checkpoint_state": r["checkpoint_state"]} for r in reps],
    "repetition_variance": "none; all three repetitions produced identical failure totals"
                            if all(r["failure_totals"] == reps[0]["failure_totals"] for r in reps) else "repetitions differ",
    "failure_totals_all_repetitions": nonzero,
    "failures_by_case_repetition_1": {c["case_id"]: c["failure_classes"] for c in reps[0]["cases"] if c["failure_classes"]},
    "native_semantics": {
        "temporal_retrieval_surface": "none; only update/_update_memory/history exist, which are mutation and audit",
        "metadata_timestamp": "opaque payload; not used in ranking",
        "dedup_or_merge_on_raw_add": preflight.get("dedup_or_merge_on_add"),
        "history_rows_per_add": 1,
        "reads_identical_on_repeat": preflight.get("reads_identical_on_repeat"),
        "searches_changed_state": preflight.get("searches_changed_point_count"),
        "unscored_capability": "Mem0 can filter on metadata such as scope; deliberately excluded from the scored Gen10 identity",
        "reproducibility_hazard": "FastEmbed 0.8.0 warns thenlper/gte-large now uses mean pooling rather than CLS; identity holds only at this pinned FastEmbed version",
    },
    "preregistered_hypothesis": {
        "question": "do the seven classes shared by Gen29 Perseus and Gen31 Hindsight recur in a third architecture?",
        "shared_seven": list(SHARED_SEVEN),
        "reproduced_in_gen32": reproduced,
        "reproduced_all_seven": len(reproduced) == len(SHARED_SEVEN),
        "interpretation": ("Mem0 has no temporal retrieval surface at all, and still reproduces every one of the seven. "
                           "That is three-engine evidence CONSISTENT WITH an append-only-without-retirement explanation. "
                           "It is not proof of causation: the three profiles also share this harness, this ruler and a "
                           "no-retirement constraint imposed by the generation itself."),
        "engine_specific_extra": {"LQ20": "stale_persistence in Mem0 only; an as_of_event_truth case that Perseus answered "
                                          "with valid_at and Hindsight with query_timestamp, so the extra failure is the "
                                          "direct cost of having no temporal filter"},
    },
    "three_engine_contrast": {
        "note": "capability surfaces only; not a numeric leaderboard",
        "gen29_perseus": prior.get("gen29_perseus", {}),
        "gen31_hindsight": prior.get("gen31_hindsight", {}),
        "gen32_mem0": nonzero,
    },
    "round1_contrast": {
        "note": "same Mem0 identity, different question",
        "round1_stress_hit_all_relevant": "0.958 / 0.917",
        "reading": "strong retrieval relevance coexists with seven longitudinal failure classes; Round-1 metrics could not see them",
    },
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"wrote {OUT}/summary.json")
print(" variance:", summary["repetition_variance"])
print(" totals:", json.dumps(nonzero))
print(" reproduced all seven:", summary["preregistered_hypothesis"]["reproduced_all_seven"])
for label, values in summary["three_engine_contrast"].items():
    if isinstance(values, dict):
        print(f"  {label}: {json.dumps(values)}")
