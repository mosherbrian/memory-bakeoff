#!/usr/bin/env python3
"""Aggregate the three Gen31 repetitions into the published summary."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import hindsight_longitudinal as H

OUT = ROOT / "results/hindsight_gen31_longitudinal"
GEN29 = ROOT / "results/perseus_vault_gen29_longitudinal/summary.json"
PREFLIGHT = ROOT / ".control-plane/gen31-preflight.json"


def _contrast(gen29_totals, gen31_totals):
    a = {k: v for k, v in gen29_totals.items() if v}
    b = {k: v for k, v in gen31_totals.items() if v}
    return {
        "note": "qualitative capability contrast only; not a numeric leaderboard",
        "gen29_perseus_totals": dict(sorted(a.items())), "gen31_hindsight_totals": dict(sorted(b.items())),
        "only_in_gen29_perseus": sorted(set(a) - set(b)),
        "only_in_gen31_hindsight": sorted(set(b) - set(a)),
        "in_both": sorted(set(a) & set(b)),
        "clean_in_both": sorted(k for k in gen31_totals if not a.get(k) and not b.get(k)),
    }

reps = [json.loads(p.read_text()) for p in sorted(OUT.glob("repetition-*.json"))]
if len(reps) != 3:
    raise SystemExit(f"expected 3 repetitions, found {len(reps)}")

totals: dict[str, int] = {}
for rep in reps:
    for name, count in rep["failure_totals"].items():
        totals[name] = totals.get(name, 0) + count

by_case: dict[str, list[str]] = {}
for record in reps[0]["cases"]:
    by_case[record["case_id"]] = record["failure_classes"]

identical = all(r["failure_totals"] == reps[0]["failure_totals"] for r in reps)
preflight = json.loads(PREFLIGHT.read_text()) if PREFLIGHT.exists() else {}
gen29 = json.loads(GEN29.read_text()) if GEN29.exists() else {}
gen29_totals = gen29.get("failure_totals_all_repetitions", {})

lifecycle_totals: dict[str, int] = {}
for rep in reps:
    for name, count in rep.get("lifecycle_failure_totals", {}).items():
        lifecycle_totals[name] = lifecycle_totals.get(name, 0) + count

summary = {
    "generation": 31,
    "status": "complete_raw_product_longitudinal_mention_time_axis_only",
    "evidence_class": "raw_product",
    "fixture_version": L.FIXTURE_VERSION, "fixture_sha256": L.fixture_sha256(),
    "scorer_version": L.SCORER_VERSION, "scorer_contract_sha256": L.scorer_contract_sha256(),
    "result_schema_version": L.RESULT_SCHEMA_VERSION,
    "adapter_version": H.ADAPTER_VERSION, "adapter_contract_sha256": H.adapter_contract_sha256(),
    "adapter_contract": H.adapter_contract_payload(),
    "system_identity": {
        "product": "hindsight", "product_version": "0.9.2",
        "source_commit": "ebad478240d3171bb88201ececda5e8d9883d22d",
        "packages": ["hindsight-all 0.9.2", "hindsight-api-slim 0.9.2", "hindsight-client 0.9.2", "hindsight-embed 0.9.2"],
        "llm_provider": "none", "raw_declaration": "HINDSIGHT_RAW_LLM_PROVIDER=none",
        "embeddings": "intfloat/multilingual-e5-small ONNX, snapshot 614241f622f53c4eeff9890bdc4f31cfecc418b3, 384 dims, mean pooling, normalized, E5 query/passage prefixes",
        "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2, local CPU",
        "database": "Homebrew PostgreSQL 17.11 + pgvector 0.8.6, fresh database and bank per repetition",
        "requested_limit": 5, "nofile": 8192,
        "reader": "none", "inference_server": "none",
    },
    "model_or_product_llm_calls": False,
    "repetitions": [{"repetition": r["repetition"], "bank": r["bank"], "cases": len(r["cases"]),
                     "checkpoints": len(r["checkpoint_state"]),
                     "provenance_exact_all_cases": all(c["provenance_exact_all"] for c in r["cases"]),
                     "failure_totals": r["failure_totals"],
                     "lifecycle_failure_totals": r["lifecycle_failure_totals"],
                     "checkpoint_state": r["checkpoint_state"]} for r in reps],
    "repetition_variance": "none; all three repetitions produced identical failure totals" if identical else "repetitions differ",
    "failure_totals_all_repetitions": {k: v for k, v in sorted(totals.items()) if v},
    "lifecycle_failure_totals_all_repetitions": {k: v for k, v in sorted(lifecycle_totals.items()) if v},
    "scorer_streams": ("case failures come from score_longitudinal_case; lifecycle failures from score_lifecycle_state; they are separate scorer outputs and must never be merged or read for each other"),
    "failures_by_case_repetition_1": {k: v for k, v in sorted(by_case.items()) if v},
    "query_side_effects": {
        "measured": True,
        "database_changed_by_reads": preflight.get("db_changed_by_reads", {}) or "no change",
        "identical_result_order_on_repeat": preflight.get("reads_return_identical_order"),
        "max_fused_score_drift": max((max(d.values()) for d in preflight.get("score_drift_between_identical_reads", []) if d), default=None),
        "isolation": "scored queries ran against the live checkpoint store; reads measured side-effect-free on unrelated data first",
    },
    "temporal_axis": {
        "native_axis_used": "mentioned_at (raw retain timestamp), preserved exactly",
        "occurred_start_end": "never populated in the raw profile",
        "why": "occurred_* is written only by LLM fact extraction, by the transfer importer replaying already-extracted facts, or by the PATCH curate endpoint that also carries invalidate/revert; all three are excluded from this profile",
        "vantage_point_read": "recall(query_timestamp=public event time)",
        "time_base": "none needed; raw retain accepts an explicit per-item timestamp so the store timeline is the fixture timeline",
    },
    "paired_contrast_gen29_perseus": _contrast(gen29_totals, totals),
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"wrote {OUT}/summary.json")
print(" variance:", summary["repetition_variance"])
print(" totals:", json.dumps(summary["failure_totals_all_repetitions"]))
c = summary["paired_contrast_gen29_perseus"]
print(" only Perseus had:", c["only_in_gen29_perseus"])
print(" only Hindsight has:", c["only_in_gen31_hindsight"])
print(" both:", c["in_both"])
print(" clean in both:", c["clean_in_both"])
