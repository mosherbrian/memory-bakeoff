#!/usr/bin/env python3
"""Gen70: the two newly reachable probes, and nothing else.

**Probe 1 - future leakage.** Ingest the WHOLE timeline through CP16, then ask
each earlier checkpoint's questions. The store now holds facts the questioner
should not yet know, so an engine that cannot filter by knowledge time will hand
one back. The frozen scorer already flags that; Gen69 proved the path fires.

**Probe 2 - unknown hallucination.** Grade the `negative_unknown` case through
`score_answer_claim`, the call Gen68 found nobody was making.

The 20-case longitudinal suite is NOT re-run. Each engine keeps its frozen
config, adapter and repetition policy, and every per-case record keeps both
clocks so these results can join the Gen68 table without rewriting history.
"""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, sys, tempfile, time
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import longitudinal as L                    # noqa: E402
from memory_bakeoff import temporal_reachability as T           # noqa: E402

OUT = ROOT / "results" / "temporal_blind_spot_gen70"
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
PROBE = T.LEAKAGE_PROBE
LIMIT = 5


def load(script: str):
    """Import a frozen runner for its helpers without running its CLI."""
    loader = SourceFileLoader(f"frozen_{Path(script).stem}", str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def probe_checkpoints(fixture) -> list[str]:
    have_cases = {c.checkpoint_id for c in fixture.cases}
    return [cp for cp in PROBE["query_as_of_checkpoints"] if cp in have_cases]


def score(fixture, records: list[dict]) -> list[dict]:
    """Score each probe record, separating leakage from ordinary retrieval."""
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        result = L.score_longitudinal_case(fixture, case, returned)
        classes = list(result.failure_classes)
        visible = {o.id for o in fixture.prefix(record["checkpoint_id"])}
        leaked = sorted(set(returned) - visible)
        record.update({
            "failure_classes": classes,
            "future_leakage": str(L.FailureClass.FUTURE_LEAKAGE) in classes,
            "leaked_observations": leaked,
            "retrieval_failure_classes": [c for c in classes
                                          if c != str(L.FailureClass.FUTURE_LEAKAGE)],
        })
    return records


# --------------------------------------------------------------------------
# mem0 2.0.19, frozen Gen32 config and adapter.
# --------------------------------------------------------------------------
def run_mem0(fixture, repetition: int, root: Path) -> dict:
    g32 = load("run_mem0_gen32_longitudinal.py")
    upstream = ROOT / "external/mem0"
    if str(upstream) not in sys.path:
        sys.path.insert(0, str(upstream))
    from mem0 import Memory
    M = g32.M

    path = str(root / f"rep{repetition}")
    memory = Memory.from_config(
        g32.config_for(path, f"memory-bakeoff-gen70-r{repetition}"))

    native_to_canonical: dict[str, str] = {}
    # Over-ingest: the entire timeline, before any question is asked.
    for observation in fixture.observations:
        payload = M.add_arguments(observation)
        M.assert_public_only(payload)
        result = memory.add(payload["text"], user_id=payload["user_id"],
                            infer=payload["infer"], metadata=payload["metadata"])
        rows = result.get("results") if isinstance(result, dict) else result
        for row in (rows or []):
            if isinstance(row, dict) and row.get("id"):
                native_to_canonical[row["id"]] = observation.id
        time.sleep(0.02)

    stored = memory.get_all(filters={"user_id": M.USER_ID})
    stored_rows = stored.get("results") if isinstance(stored, dict) else stored
    for row in (stored_rows or []):
        marker = (row.get("metadata") or {}).get("record_id")
        if marker:
            native_to_canonical.setdefault(row.get("id"), marker)

    records = []
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    for checkpoint_id in probe_checkpoints(fixture):
        prefix_sha = hashlib.sha256(L.canonical_json(
            [o.public_dict() for o in fixture.prefix(checkpoint_id)]).encode()).hexdigest()
        for case in cases_by_checkpoint.get(checkpoint_id, []):
            arguments = M.search_arguments(case, LIMIT)
            started = time.perf_counter()
            raw = memory.search(arguments["query"], filters=arguments["filters"],
                                limit=arguments["limit"], threshold=arguments["threshold"])
            latency_ms = (time.perf_counter() - started) * 1000
            hits = raw.get("results") if isinstance(raw, dict) else raw
            items = []
            for rank, hit in enumerate((hits or [])[:LIMIT], start=1):
                metadata = hit.get("metadata") or {}
                marker = metadata.get("record_id")
                canonical = native_to_canonical.get(hit.get("id"))
                exact = canonical is not None and marker == canonical
                items.append({"native_rank": rank, "native_id": hit.get("id"),
                              "record_id": marker,
                              "canonical_id": canonical if exact else None,
                              "provenance_exact": exact, "score": hit.get("score"),
                              "text": (hit.get("memory") or hit.get("text") or "")[:110]})
            records.append({
                "case_id": case.id, "checkpoint_id": checkpoint_id,
                "queried_as_of": checkpoint_id,
                "ingested_through": PROBE["ingest_through_checkpoint"],
                "ingested_prefix_sha256": prefix_sha,
                "native_temporal_operation": M.native_operation(case),
                "requested_limit": LIMIT, "latency_ms": round(latency_ms, 2),
                "returned": items,
                "provenance_exact_all": all(i["provenance_exact"] for i in items),
                "reader_answer": None,
            })
    return {"records": score(fixture, records),
            "observations_ingested": len(fixture.observations)}


ENGINES = {"mem0": run_mem0}


def answer_claim_probe(fixture, records: list[dict]) -> dict:
    """Probe 2. These adapters retrieve; they never assert.

    That is not a clean score. An engine with no answer surface cannot be
    charged with hallucinating one, so the class is NOT_APPLICABLE for this
    configuration - the same distinction Gen68 drew between a real zero and an
    unmeasurable one.
    """
    case = next(c for c in fixture.cases
                if c.target_kind is L.TargetKind.NEGATIVE_UNKNOWN)
    answers = [r for r in records if r.get("reader_answer") is not None]
    if not answers:
        return {
            "case_id": case.id,
            "status": "NOT_APPLICABLE",
            "why": "the frozen adapter exposes retrieval only (search/recall); it "
                   "returns evidence and never asserts an answer, so there is no "
                   "claim to grade",
            "reader_answers_seen": 0,
            "graded": [],
            "not_a_clean_zero": True,
        }
    graded = [T.grade_negative_unknown(
        r["reader_answer"], expected_ids=case.expected_ids,
        score_answer_claim=L.score_answer_claim, case=case) for r in answers]
    return {"case_id": case.id, "status": "GRADED",
            "reader_answers_seen": len(graded),
            "graded": [{**g, "failure_classes": list(g["failure_classes"])}
                       for g in graded],
            "hallucinations": sum(
                1 for g in graded
                if str(L.FailureClass.UNKNOWN_HALLUCINATION) in g["failure_classes"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=sorted(ENGINES))
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()

    fixture = L.build_longitudinal_fixture()
    if L.fixture_sha256(fixture) != FIXTURE_SHA:
        raise SystemExit("fixture changed; refusing to run")

    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"gen70-{args.engine}-"))
    repetitions = []
    for repetition in range(1, args.repetitions + 1):
        payload = ENGINES[args.engine](fixture, repetition, root)
        payload["repetition"] = repetition
        payload["unknown_hallucination"] = answer_claim_probe(fixture, payload["records"])
        repetitions.append(payload)
        leaks = sum(1 for r in payload["records"] if r["future_leakage"])
        print(f"{args.engine} rep{repetition}: {len(payload['records'])} probe cases, "
              f"{leaks} with future leakage, "
              f"answer-claim {payload['unknown_hallucination']['status']}", flush=True)

    summary = {
        "engine": args.engine,
        "generation": 70,
        "probe": PROBE,
        "fixture_sha256": FIXTURE_SHA,
        "suite_rerun": False,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "future_leakage_cases": sum(1 for rep in repetitions
                                    for r in rep["records"] if r["future_leakage"]),
        "probe_cases_total": sum(len(rep["records"]) for rep in repetitions),
    }
    (OUT / f"{args.engine}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("engine", "future_leakage_cases", "probe_cases_total")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
