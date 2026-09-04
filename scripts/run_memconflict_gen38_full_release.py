#!/usr/bin/env python3
"""Gen38: full-release MemConflict pass for one engine, calibration gate first.

Persona is the atomic unit. Each persona's leaf is written temp-then-rename with
its own scientific digest, so an interrupted run resumes at persona granularity
and never mid-persona. Adapters are the frozen Gen37 contracts, asserted here.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff import memconflict_engines as E
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.providers import mem0_memconflict as MEM0A
from memory_bakeoff.providers import perseus_memconflict as PERSA
from memory_bakeoff.round2_reporting import ReportingError

ADAPTERS = {"perseus": PERSA, "mem0": MEM0A}
FROZEN_ADAPTER_SHA = {
    "perseus": "627f812d5296130cdee5062ee48a9690a8873e635ee5683c8dd51432fd0e2c99",
    "mem0": "920f496be7470fca3bb5da4fb26b6bde6b9a13214ba5b934d875b06e97e0d190",
}
CONTRACT_SHA = "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28"
LEAF_SCHEMA = "memconflict-gen38-leaf-v1"
AUDIT_EVERY_NTH_SESSION = 5
REPEAT_MODULUS = 37


def stable_bucket(text: str, modulus: int) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16) % modulus


def leaf_digest(leaf: dict) -> str:
    """Scientific content only: released session identities, ranks, applicability.

    Native ids, scores and every wall-clock measurement are excluded, so the
    digest is reproducible across runs of the same engine on the same release.
    """
    content = {
        "schema": LEAF_SCHEMA,
        "engine": leaf["engine"],
        "persona_id": leaf["persona_id"],
        "adapter_sha256": leaf["adapter_sha256"],
        "questions": [
            {"question_key": record["question_key"],
             "returned_sessions": [item["session_id"] for item in record["returned"]],
             "provenance_status": [item["provenance_status"] for item in record["returned"]]}
            for record in leaf["questions"]
        ],
    }
    return hashlib.sha256(canonical_json(content).encode()).hexdigest()


def persona_is_complete(path: Path, engine: str, persona: dict) -> bool:
    """A persona may be skipped only if its leaf validates against every pin."""
    if not path.exists():
        return False
    try:
        leaf = json.loads(path.read_text())
    except json.JSONDecodeError:
        return False
    expected_writes = len(M.ingestion_units(persona))
    expected_questions = len(M.questions(persona))
    checks = (
        leaf.get("schema") == LEAF_SCHEMA,
        leaf.get("engine") == engine,
        leaf.get("persona_id") == persona["ID"],
        leaf.get("adapter_sha256") == FROZEN_ADAPTER_SHA[engine],
        leaf.get("contract_sha256") == CONTRACT_SHA,
        leaf.get("dataset_sha256") == M.DATASET_SHA256,
        leaf.get("operations", {}).get("expected_valid_messages") == expected_writes,
        len(leaf.get("questions") or []) == expected_questions,
        leaf.get("leaf_digest") == leaf_digest(leaf),
    )
    return all(checks)


def run_persona(engine_name: str, persona: dict, root: Path) -> tuple[dict, dict]:
    adapter = ADAPTERS[engine_name]
    if adapter.adapter_contract_sha256() != FROZEN_ADAPTER_SHA[engine_name]:
        raise ReportingError(f"{engine_name} adapter drifted from the frozen Gen37 contract")

    engine = E.ENGINES[engine_name](persona["ID"], root)
    units, anomalies = M.parse_dialogue(persona)
    by_session: dict[int, list] = {}
    for unit in units:
        by_session.setdefault(unit.session_index, []).append(unit)
    questions_by_session: dict[int, list] = {}
    for question in M.questions(persona):
        questions_by_session.setdefault(question.session_index, []).append(question)

    ledger: dict[str, dict] = {}
    write_times, query_times = E.Timings(), E.Timings()
    records, audits, repeats = [], [], []
    write_actions: collections.Counter = collections.Counter()
    quarantined: list[dict] = []
    write_failures: list[dict] = []
    started_all = time.perf_counter()

    for session_index, session in enumerate(persona["Full_Session_Chain"]):
        for unit in by_session.get(session_index, []):
            try:
                native_id, latency, action = engine.write(unit.text)
            except Exception as exc:
                write_failures.append({"provenance": unit.provenance_id, "error": str(exc)[:300]})
                continue
            write_times.add(latency)
            write_actions[action] += 1
            # Gen38 instrumentation: a non-normal admission is recorded WITH its
            # provenance, so the support-availability diagnostic can be joined later.
            if action not in ("created", "ADD"):
                quarantined.append({"provenance": unit.provenance_id, "session_id": unit.session_id,
                                    "action": action})
            ledger[native_id] = {"persona_id": unit.persona_id, "session_id": unit.session_id,
                                 "session_index": unit.session_index, "turn": unit.turn_index,
                                 "message": unit.message_index}

        session_questions = questions_by_session.get(session_index, [])
        if not session_questions:
            continue

        audit = stable_bucket(str(session["Session_ID"]), AUDIT_EVERY_NTH_SESSION) == 0
        digest_before = engine.state_digest() if audit else None
        engine.open_read_snapshot()
        try:
            for question in session_questions:
                items, latency = engine.search(question.text)
                query_times.add(latency)
                returned = []
                for item in items:
                    entry = ledger.get(item["native_id"])
                    returned.append({
                        "rank": item["rank"], "score": item["score"],
                        "provenance_status": "mapped" if entry else "unmapped_provenance",
                        "session_id": entry["session_id"] if entry else None,
                        "session_index": entry["session_index"] if entry else None,
                        "turn": entry["turn"] if entry else None,
                        "message": entry["message"] if entry else None,
                    })
                future = [r for r in returned
                          if r["session_index"] is not None and r["session_index"] > question.session_index]
                if future:
                    raise ReportingError(f"{engine_name} {question.key}: future-session leakage {future}")
                records.append({"question_key": question.key, "question_id": question.question_id,
                                "session_id": question.session_id, "session_index": question.session_index,
                                "returned": returned, "returned_count": len(returned),
                                "latency_ms": round(latency, 3)})
                # repeat immediately, against this same session-consistent snapshot
                if stable_bucket(question.key, REPEAT_MODULUS) == 0:
                    again, _ = engine.search(question.text)
                    mapped_again = [(ledger.get(i["native_id"]) or {}).get("session_id") for i in again]
                    repeats.append({
                        "question_key": question.key,
                        "same_session_order": [r["session_id"] for r in returned] == mapped_again,
                        "same_scores": [r["score"] for r in returned] == [i["score"] for i in again],
                        "snapshot": "same_session_boundary",
                    })
        finally:
            engine.close_read_snapshot()
        if audit:
            audits.append({"session_id": session["Session_ID"], "digest_before": digest_before,
                           "digest_after": engine.state_digest(), "questions": len(session_questions)})

    inventory = engine.inventory()
    store_bytes = engine.store_bytes()
    operations = {
        "expected_valid_messages": len(units),
        "malformed_excluded": len(anomalies),
        "successful_writes": sum(write_actions.values()),
        "distinct_native_ids": len(ledger),
        "write_actions": dict(write_actions),
        "quarantined_writes": quarantined,
        "write_failures": write_failures,
        "write_latency": write_times.summary(),
        "query_latency": query_times.summary(),
        "questions_executed": len(records),
        "wall_seconds": round(time.perf_counter() - started_all, 2),
        "store_bytes": store_bytes,
        "bytes_per_write": round(store_bytes / max(1, len(ledger)), 1),
    }
    engine.close()

    leaf = {
        "schema": LEAF_SCHEMA,
        "engine": engine_name,
        "persona_id": persona["ID"],
        "adapter_version": adapter.ADAPTER_VERSION,
        "adapter_sha256": adapter.adapter_contract_sha256(),
        "contract_sha256": M.contract_sha256(),
        "dataset_sha256": M.DATASET_SHA256,
        "upstream_commit": M.UPSTREAM_COMMIT,
        "questions": records,
        "read_side_effect_audit": audits,
        "deterministic_repeats": repeats,
        "inventory": inventory,
        "operations": operations,
        "ledger_size": len(ledger),
    }
    leaf["leaf_digest"] = leaf_digest(leaf)
    return leaf, ledger


def write_atomic(path: Path, payload: dict) -> None:
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(temp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", choices=sorted(E.ENGINES), required=True)
    ap.add_argument("--slice", choices=("calibration", "heldout", "all"), default="all")
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen38_full_release"))
    ap.add_argument("--state-root", default="/private/tmp")
    args = ap.parse_args()

    if M.dataset_sha256() != M.DATASET_SHA256:
        raise ReportingError("pinned dataset hash drift; refusing to run")
    if M.contract_sha256() != CONTRACT_SHA:
        raise ReportingError("frozen benchmark contract drifted; refusing to run")

    personas = M.load_personas()
    manifest = json.loads((ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text())
    calibration = set(manifest["calibration_persona_ids"])
    if calibration != set(M.calibration_personas([p["ID"] for p in personas])):
        raise ReportingError("calibration manifest drifted from the frozen selection")

    if args.slice == "calibration":
        selected = [p for p in personas if p["ID"] in calibration]
    elif args.slice == "heldout":
        selected = [p for p in personas if p["ID"] not in calibration]
    else:
        selected = ([p for p in personas if p["ID"] in calibration]
                    + [p for p in personas if p["ID"] not in calibration])

    out = Path(args.out) / args.engine
    out.mkdir(parents=True, exist_ok=True)
    state_root = Path(args.state_root) / f"memconflict-gen38-{args.engine}"
    state_root.mkdir(parents=True, exist_ok=True)

    for index, persona in enumerate(selected, start=1):
        leaf_path = out / f"persona-{persona['ID']}.json"
        if persona_is_complete(leaf_path, args.engine, persona):
            print(f"[{index}/{len(selected)}] {args.engine} {persona['ID'][:12]}: leaf validated, skipping",
                  flush=True)
            continue
        for stale in (leaf_path, leaf_path.with_suffix(".json.tmp"),
                      out / f"ledger-{persona['ID']}.json"):
            if stale.exists():
                stale.unlink()
        for stale_store in (state_root / f"{args.engine}-{persona['ID']}",
                            state_root / f"perseus-snap-{persona['ID']}"):
            if stale_store.exists():
                import shutil
                shutil.rmtree(stale_store)

        leaf, ledger = run_persona(args.engine, persona, state_root)
        write_atomic(leaf_path, leaf)
        write_atomic(out / f"ledger-{persona['ID']}.json", ledger)
        ops = leaf["operations"]
        print(f"[{index}/{len(selected)}] {args.engine} {persona['ID'][:12]}: "
              f"{ops['successful_writes']} writes, {ops['questions_executed']} questions, "
              f"{ops['wall_seconds']}s, write p50 {ops['write_latency'].get('p50_ms')}ms, "
              f"query p50 {ops['query_latency'].get('p50_ms')}ms, "
              f"quarantined {len(ops['quarantined_writes'])}, digest {leaf['leaf_digest'][:12]}",
              flush=True)
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
