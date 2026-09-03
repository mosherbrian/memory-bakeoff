#!/usr/bin/env python3
"""Gen33: agentmemory 0.9.29 against longitudinal-v1, with native supersession enabled."""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
loader = SourceFileLoader("g13", str(ROOT / "scripts/run_agentmemory_gen13.py"))
spec = importlib.util.spec_from_loader("g13", loader)
g13 = importlib.util.module_from_spec(spec)
loader.exec_module(g13)

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import agentmemory_longitudinal as A

AGENTMEMORY = ROOT / "external/agentmemory"
LIMIT = 5
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"


def native_rows(base, agent):
    rows = g13.isolated_rows(base, agent)
    return rows.get("results") or rows.get("memories") or []


def run_repetition(fixture, repetition: int, instance: int) -> dict:
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen33-r{repetition}-", dir="/private/tmp"))
    agent = f"memory-bakeoff-gen33-r{repetition}"
    truth = {o.id: {"corrects_id": o.corrects_id, "supersedes_id": o.supersedes_id} for o in fixture.observations}
    checkpoints = {c.ingestion_order: c for c in fixture.checkpoints}
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    native_to_canonical: dict[str, str] = {}
    records, checkpoint_state, lifecycle_by_checkpoint = [], {}, {}
    supersession_events: list[dict] = []
    launcher = None
    try:
        base, startup, launcher = g13.start_service(AGENTMEMORY, state, instance, agent)
        for observation in fixture.observations:
            payload = A.remember_arguments(observation, agent)
            A.assert_public_only(payload)
            before = {r.get("id"): r for r in native_rows(base, agent)}
            g13.request_json(base, "/agentmemory/remember", body=payload)
            time.sleep(0.05)
            after = native_rows(base, agent)
            for row in after:
                for source in (row.get("sourceObservationIds") or []):
                    native_to_canonical[row.get("id")] = source
            # capture retirements this write caused, from native fields only
            for row in after:
                previous = before.get(row.get("id"))
                if row.get("isLatest") is False and (previous is None or previous.get("isLatest") is not False):
                    predecessor = native_to_canonical.get(row.get("id"))
                    successor_row = next((r for r in after if row.get("id") in (r.get("supersedes") or [])), None)
                    successor = native_to_canonical.get(successor_row.get("id")) if successor_row else None
                    supersession_events.append({
                        "at_ingestion_order": observation.ingestion_order,
                        "predecessor_native_id": row.get("id"), "predecessor_canonical_id": predecessor,
                        "successor_native_id": successor_row.get("id") if successor_row else None,
                        "successor_canonical_id": successor,
                        "successor_version": successor_row.get("version") if successor_row else None,
                        "classification": A.classify_supersession(predecessor, successor, truth),
                    })

            checkpoint = checkpoints.get(observation.ingestion_order)
            if checkpoint is None:
                continue

            rows = native_rows(base, agent)
            live = {native_to_canonical.get(r.get("id")) for r in rows if r.get("isLatest") is not False}
            in_kv = {native_to_canonical.get(r.get("id")) for r in rows}
            prefix_ids = {o.id for o in fixture.prefix(checkpoint.id)}
            checkpoint_state[checkpoint.id] = {
                "rows_total": len(rows),
                "rows_live": sum(1 for r in rows if r.get("isLatest") is not False),
                "rows_retired": sum(1 for r in rows if r.get("isLatest") is False),
                "expected_prefix": len(prefix_ids),
                "supersessions_so_far": len(supersession_events),
            }
            lifecycle_by_checkpoint[checkpoint.id] = [
                L.LifecycleEvidence(cid, active_current=cid in live,
                                    historically_recoverable=True if cid in in_kv else None,
                                    disposition=L.LifecycleDisposition.ACTIVE_CURRENT if cid in live
                                    else (L.LifecycleDisposition.RETIRED_SUPERSEDED if cid in in_kv
                                          else L.LifecycleDisposition.UNKNOWN),
                                    evidence_strength="native_memory_row",
                                    native_evidence=f"isLatest={cid in live}; present_in_kv={cid in in_kv}")
                for cid in sorted(prefix_ids)]

            prefix_sha = hashlib.sha256(L.canonical_json([o.public_dict() for o in fixture.prefix(checkpoint.id)]).encode()).hexdigest()
            for case in cases_by_checkpoint.get(checkpoint.id, []):
                arguments = A.search_arguments(case, agent, LIMIT)
                started = time.perf_counter()
                raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
                latency_ms = (time.perf_counter() - started) * 1000
                items = []
                for rank, hit in enumerate((raw.get("results") or [])[:LIMIT], start=1):
                    obs = hit.get("obsId")
                    canonical = native_to_canonical.get(obs) or (hit.get("sourceObservationIds") or [None])[0]
                    exact = canonical in {o.id for o in fixture.observations}
                    items.append({"native_rank": rank, "obsId": obs,
                                  "canonical_id": canonical if exact else None, "provenance_exact": exact,
                                  "score": hit.get("score"), "text": (hit.get("content") or "")[:110]})
                records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                                "ingested_prefix_sha256": prefix_sha,
                                "native_temporal_operation": A.native_operation(case),
                                "requested_limit": LIMIT, "latency_ms": round(latency_ms, 2),
                                "returned": items,
                                "provenance_exact_all": all(i["provenance_exact"] for i in items)})
    finally:
        if launcher is not None:
            g13.stop_service(AGENTMEMORY, state, instance, agent, launcher)

    case_scores = []
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        score = L.score_longitudinal_case(fixture, case, returned)
        record["failure_classes"] = list(score.failure_classes)
        case_scores.append(score)
    lifecycle_scores = [L.score_lifecycle_state(fixture, cid, ev) for cid, ev in lifecycle_by_checkpoint.items()]

    return {"repetition": repetition, "agent_id": agent, "cases": records,
            "checkpoint_state": checkpoint_state,
            "supersession_events": supersession_events,
            "supersession_count": len(supersession_events),
            "supersession_classification": {k: sum(1 for e in supersession_events if e["classification"] == k)
                                            for k in ("legitimate_supersession", "false_supersession", "unmapped")},
            "lifecycle": {cid: [{"canonical_id": e.canonical_id, "active_current": e.active_current,
                                 "historically_recoverable": e.historically_recoverable,
                                 "disposition": str(e.disposition)} for e in ev]
                          for cid, ev in lifecycle_by_checkpoint.items()},
            "lifecycle_failures": {s.checkpoint_id: list(s.failure_classes) for s in lifecycle_scores},
            "failure_totals": L.aggregate_failure_classes(case_scores),
            "lifecycle_failure_totals": L.aggregate_failure_classes(lifecycle_scores)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--out", default=str(ROOT / "results/agentmemory_gen33_longitudinal"))
    args = parser.parse_args()
    if L.fixture_sha256() != FIXTURE_SHA or L.scorer_contract_sha256() != SCORER_SHA:
        raise SystemExit("frozen ruler hash drift; refusing to run")
    fixture = L.build_longitudinal_fixture()
    reps = [run_repetition(fixture, n, 30 + n) for n in range(1, args.repetitions + 1)]
    if L.fixture_sha256() != FIXTURE_SHA:
        raise SystemExit("fixture hash drifted during the run")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for rep in reps:
        (out / f"repetition-{rep['repetition']}.json").write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    for rep in reps:
        failing = {k: v for k, v in rep["failure_totals"].items() if v}
        print(f"  rep{rep['repetition']}: {len(rep['cases'])} cases, supersessions {rep['supersession_count']} "
              f"{rep['supersession_classification']}, failures {failing or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
