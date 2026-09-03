#!/usr/bin/env python3
"""Gen36 diagnostic pilot: prove the MemConflict plumbing, score no contestant.

Only benchmark-owned providers run here: a null provider, the existing BM25
baseline over the allowed history prefix, and a deliberately illegal provider that
returns a future session so the harness can be shown to reject it. No memory
product, no reader, no LLM, no GPU.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.models import MemoryRecord, QueryCase
from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.round2_reporting import ReportingError, Status

TOP_K = max(M.UPSTREAM_TOP_K_VALUES)


def allowed_units(units: list[M.Unit], question: M.Question) -> list[M.Unit]:
    allowed = M.allowed_session_indices(question)
    return [u for u in units if u.session_index in allowed]


def null_provider(units: list[M.Unit], question: M.Question) -> list[M.Unit]:
    return []


def bm25_provider(units: list[M.Unit], question: M.Question) -> list[M.Unit]:
    visible = allowed_units(units, question)
    if not visible:
        return []
    by_id = {u.provenance_id: u for u in visible}
    records = [MemoryRecord(id=u.provenance_id, text=u.text,
                            timestamp=datetime.fromisoformat(u.date), session_id=str(u.session_id))
               for u in visible]
    provider = BM25Provider()
    provider.ingest(records)
    result = provider.retrieve(QueryCase(id=question.key, category="memconflict", query=question.text,
                                         relevant_ids=()), top_k=TOP_K)
    return [by_id[item.record_id] for item in result.items if item.record_id in by_id]


def future_leak_provider(units: list[M.Unit], question: M.Question) -> list[M.Unit]:
    """Deliberately illegal: returns a unit the question is not allowed to see."""
    future = [u for u in units if u.session_index > question.session_index]
    return future[:1]


PROVIDERS = {"null": null_provider, "bm25_baseline": bm25_provider}


def score(persona: dict, units: list[M.Unit], provider) -> dict:
    per_question = []
    totals = {"present": 0, "measured_zero": 0, "unmeasured": 0}
    hits = {k: {"hit": 0, "scored": 0} for k in M.UPSTREAM_TOP_K_VALUES}
    for question in M.questions(persona):
        returned = provider(units, question)
        M.assert_within_boundary(question, returned)
        gold = M.gold_for(persona, question)
        rank = M.first_support_rank(returned, gold)
        row = {"question_key": question.key, "conflict_type": gold.conflict_type,
               "returned": [u.provenance_id for u in returned],
               "first_support_rank": rank.payload()}
        for k in M.UPSTREAM_TOP_K_VALUES:
            hit = M.hit_at_k(rank, k)
            row[f"hit_at_{k}"] = hit.payload()
            row[f"log_rank_at_{k}"] = M.log_rank_at_k(rank, k)
            if hit.status is not Status.UNMEASURED:
                hits[k]["scored"] += 1
                hits[k]["hit"] += hit.value_or_raise()
        totals[str(rank.status).replace("measured_zero", "measured_zero")] = totals.get(str(rank.status), 0) + 1
        per_question.append(row)
    return {"persona_id": persona["ID"], "questions": per_question,
            "rank_status_totals": totals,
            "hit_at_k": {str(k): v for k, v in hits.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen36_pilot"))
    args = ap.parse_args()

    if M.dataset_sha256() != M.DATASET_SHA256:
        raise ReportingError("pinned dataset hash drift; refusing to run")
    personas = M.load_personas()
    calibration = set(M.calibration_personas([p["ID"] for p in personas]))
    subset = [p for p in personas if p["ID"] in calibration]
    if not subset:
        raise ReportingError("calibration subset resolved to zero personas")

    checks: dict[str, object] = {}
    leaves: dict[str, list] = {}
    for name, provider in PROVIDERS.items():
        leaves[name] = [score(p, M.ingestion_units(p), provider) for p in subset]

    # the null provider must produce MEASURED_ZERO where gold exists, never UNMEASURED
    null_statuses = {tuple(sorted(leaf["rank_status_totals"].items())) for leaf in leaves["null"]}
    checks["null_is_measured_zero_where_gold_exists"] = all(
        leaf["rank_status_totals"].get("present", 0) == 0 and leaf["rank_status_totals"].get("measured_zero", 0) > 0
        for leaf in leaves["null"])
    checks["null_unmeasured_matches_unmappable_gold"] = all(
        leaf["rank_status_totals"].get("unmeasured", 0) > 0 for leaf in leaves["null"])
    checks["baseline_retrieves_something"] = any(
        any(row["returned"] for row in leaf["questions"]) for leaf in leaves["bm25_baseline"])
    checks["baseline_hits_some_gold"] = any(
        leaf["hit_at_k"]["3"]["hit"] > 0 for leaf in leaves["bm25_baseline"])

    # the illegal provider must be caught by the boundary assertion, not scored
    persona = subset[0]
    units = M.ingestion_units(persona)
    early = next(q for q in M.questions(persona) if q.session_index < len(persona["Full_Session_Chain"]) - 1)
    try:
        M.assert_within_boundary(early, future_leak_provider(units, early))
        checks["future_session_rejected"] = False
    except ReportingError:
        checks["future_session_rejected"] = True

    # a scorer-only field must never survive an adapter payload
    try:
        M.assert_public_only({"agent": "x", "content": "hello", "answer": "gold"})
        checks["gold_answer_rejected"] = False
    except ReportingError:
        checks["gold_answer_rejected"] = True
    try:
        M.assert_public_only({"query": early.text, "metadata": {"conflict_type": "static_conflict"}})
        checks["conflict_label_rejected"] = False
    except ReportingError:
        checks["conflict_label_rejected"] = True

    payload = {"calibration_persona_ids": sorted(calibration), "providers": sorted(PROVIDERS),
               "leaves": leaves, "checks": checks,
               "contract_sha256": M.contract_sha256(),
               "note": "diagnostic only; no memory product was run and no contestant score exists"}
    digest = hashlib.sha256(canonical_json({k: v for k, v in payload.items() if k != "note"}).encode()).hexdigest()
    payload["content_digest"] = digest

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pilot.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (out / "validation.json").write_text(json.dumps(
        {"checks": checks, "passed": all(checks.values()), "content_digest": digest},
        indent=2, sort_keys=True) + "\n")
    (out / "content-digest.txt").write_text(digest + "\n")

    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    for name in PROVIDERS:
        scored = sum(leaf["hit_at_k"]["3"]["scored"] for leaf in leaves[name])
        hit = sum(leaf["hit_at_k"]["3"]["hit"] for leaf in leaves[name])
        print(f"  {name}: hit@3 {hit}/{scored} scored questions")
    print(f"content digest {digest}")
    if not all(checks.values()):
        raise SystemExit("gen36 pilot checks failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
