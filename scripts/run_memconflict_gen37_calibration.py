#!/usr/bin/env python3
"""Gen37: one calibration pass per engine over the frozen three-persona subset.

Development-exposed calibration, not an official MemConflict score. Writes and
queries follow the frozen contract exactly; scoring happens later, in the report
builder, from these leaves.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff import memconflict_engines as E
from memory_bakeoff.providers import mem0_memconflict as MEM0A
from memory_bakeoff.providers import perseus_memconflict as PERSA
from memory_bakeoff.round2_reporting import ReportingError

ADAPTERS = {"perseus": PERSA, "mem0": MEM0A}
FROZEN_ADAPTER_SHA = {
    "perseus": "627f812d5296130cdee5062ee48a9690a8873e635ee5683c8dd51432fd0e2c99",
    "mem0": "920f496be7470fca3bb5da4fb26b6bde6b9a13214ba5b934d875b06e97e0d190",
}
AUDIT_EVERY_NTH_SESSION = 5
REPEAT_MODULUS = 37


def stable_bucket(text: str, modulus: int) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16) % modulus


def run_persona(engine_name: str, persona: dict, root: Path) -> dict:
    engine = E.ENGINES[engine_name](persona["ID"], root)
    adapter = ADAPTERS[engine_name]
    if adapter.adapter_contract_sha256() != FROZEN_ADAPTER_SHA[engine_name]:
        raise ReportingError(f"{engine_name} adapter drifted after preflight freeze")

    units, anomalies = M.parse_dialogue(persona)
    by_session: dict[int, list] = {}
    for unit in units:
        by_session.setdefault(unit.session_index, []).append(unit)
    questions_by_session: dict[int, list] = {}
    for question in M.questions(persona):
        questions_by_session.setdefault(question.session_index, []).append(question)

    ledger: dict[str, dict] = {}
    write_times, query_times = E.Timings(), E.Timings()
    records: list[dict] = []
    audits: list[dict] = []
    repeats: list[dict] = []
    replacements: list[dict] = []
    write_failures: list[dict] = []
    write_actions: collections.Counter = collections.Counter()
    started_all = time.perf_counter()

    for session_index, session in enumerate(persona["Full_Session_Chain"]):
        for unit in by_session.get(session_index, []):
            try:
                native_id, latency, action = engine.write(unit.text)
            except Exception as exc:  # recorded, never silently dropped
                write_failures.append({"provenance": unit.provenance_id, "error": str(exc)[:300]})
                continue
            write_times.add(latency)
            write_actions[action] += 1
            if native_id in ledger:
                # the product returned an id it had already issued: a native replacement,
                # recorded rather than overwritten, because it changes what the store holds
                replacements.append({"native_id": native_id, "previous": ledger[native_id],
                                     "now": unit.provenance_id, "action": action})
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
                        "rank": item["rank"],
                        "score": item["score"],
                        "provenance_status": "mapped" if entry else "unmapped_provenance",
                        "session_id": entry["session_id"] if entry else None,
                        "session_index": entry["session_index"] if entry else None,
                        "turn": entry["turn"] if entry else None,
                        "message": entry["message"] if entry else None,
                    })
                future = [r for r in returned
                          if r["session_index"] is not None and r["session_index"] > question.session_index]
                if future:
                    raise ReportingError(
                        f"{engine_name} {question.key}: future-session leakage {future}")
                records.append({"question_key": question.key, "question_id": question.question_id,
                                "session_id": question.session_id, "session_index": question.session_index,
                                "returned": returned, "returned_count": len(returned),
                                "latency_ms": round(latency, 3)})
                # label-blind repeat, against the SAME unchanged state this query just saw
                if stable_bucket(question.key, REPEAT_MODULUS) == 0:
                    again, _ = engine.search(question.text)
                    mapped_again = [(ledger.get(i["native_id"]) or {}).get("session_id") for i in again]
                    repeats.append({
                        "question_key": question.key,
                        "same_session_order": [r["session_id"] for r in returned] == mapped_again,
                        "same_scores": [r["score"] for r in returned] == [i["score"] for i in again],
                    })
        finally:
            engine.close_read_snapshot()
        if audit:
            audits.append({"session_id": session["Session_ID"], "digest_before": digest_before,
                           "digest_after": engine.state_digest(),
                           "questions": len(session_questions)})

    inventory = engine.inventory()
    operations = {
        "expected_valid_messages": len(units),
        "malformed_excluded": len(anomalies),
        "attempted_writes": len(units),
        "successful_writes": sum(write_actions.values()),
        "distinct_native_ids": len(ledger),
        "write_actions": dict(write_actions),
        "native_id_replacements": replacements,
        "write_failures": write_failures,
        "write_latency": write_times.summary(),
        "query_latency": query_times.summary(),
        "questions_executed": len(records),
        "wall_seconds": round(time.perf_counter() - started_all, 2),
        "store_bytes": engine.store_bytes(),
        "bytes_per_write": round(engine.store_bytes() / max(1, len(ledger)), 1),
        "duplicate_message_texts": len(units) - len({u.text for u in units}),
    }
    engine.close()

    return {
        "engine": engine_name,
        "persona_id": persona["ID"],
        "adapter_version": adapter.ADAPTER_VERSION,
        "adapter_sha256": adapter.adapter_contract_sha256(),
        "questions": records,
        "read_side_effect_audit": audits,
        "deterministic_repeats": repeats,
        "inventory": inventory,
        "operations": operations,
        "ledger_size": len(ledger),
    }, ledger


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", choices=sorted(E.ENGINES), required=True)
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen37_calibration"))
    ap.add_argument("--state-root", default="/private/tmp")
    args = ap.parse_args()

    if M.dataset_sha256() != M.DATASET_SHA256:
        raise ReportingError("pinned dataset hash drift; refusing to run")
    if M.contract_sha256() != "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28":
        raise ReportingError("frozen benchmark contract drifted; refusing to run")

    personas = M.load_personas()
    manifest = json.loads((ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text())
    calibration = set(manifest["calibration_persona_ids"])
    subset = [p for p in personas if p["ID"] in calibration]
    if len(subset) != manifest["calibration_persona_count"]:
        raise ReportingError("calibration subset does not match the frozen manifest")

    out = Path(args.out) / args.engine
    out.mkdir(parents=True, exist_ok=True)
    state_root = Path(args.state_root) / f"memconflict-gen37-{args.engine}-{int(time.time())}"
    state_root.mkdir(parents=True)

    for persona in subset:
        leaf, ledger = run_persona(args.engine, persona, state_root)
        (out / f"persona-{persona['ID']}.json").write_text(json.dumps(leaf, indent=2, sort_keys=True) + "\n")
        (out / f"ledger-{persona['ID']}.json").write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
        ops = leaf["operations"]
        print(f"{args.engine} {persona['ID']}: {ops['successful_writes']}/{ops['attempted_writes']} writes, "
              f"{ops['questions_executed']} questions, {ops['wall_seconds']}s, "
              f"write p50 {ops['write_latency'].get('p50_ms')}ms, query p50 {ops['query_latency'].get('p50_ms')}ms, "
              f"store {round(ops['store_bytes'] / 1e6, 1)}MB")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
