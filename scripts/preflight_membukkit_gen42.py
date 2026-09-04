#!/usr/bin/env python3
"""Gen42 preflight: freeze the MemBukkit MemConflict adapter before exposure.

Synthetic content only. No benchmark fixture is opened anywhere in this file,
and the frozen calibration personas are never touched.
"""
from __future__ import annotations

import argparse, importlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict_engines_gen42 as G42  # noqa: E402
from memory_bakeoff.membukkit_gen41 import CONFIGURATIONS  # noqa: E402
from memory_bakeoff.providers import membukkit_memconflict as ADAPTER  # noqa: E402
from memory_bakeoff.round2_reporting import ReportingError  # noqa: E402

G37 = importlib.import_module("run_memconflict_gen37_calibration")

# Invented content, written before any product output was observed, unrelated to
# every corpus in this repository. Two messages share text on purpose.
SHARED_TEXT = "The kiln in the pottery annexe is fired on alternate Thursdays."
SYNTHETIC_PERSONA = {
    "ID": "SYN-PREFLIGHT",
    "Full_Session_Chain": [
        {
            "Session_ID": "SYN-S1",
            "Date": "2031-01-05",
            "Session_Dialogue": {
                "dialogue_turn_1": [
                    {"role": "user", "content": "The annexe stores its glazes on the north wall."},
                    {"role": "assistant", "content": SHARED_TEXT},
                ],
                "dialogue_turn_2": [
                    {"role": "user", "content": "Bisque firing runs at a lower temperature than glaze firing."},
                    {"role": "malformed"},
                ],
            },
            "Session_Questions": [
                {"question_id": "SYN-Q1", "question": "Where are the glazes kept?"},
            ],
        },
        {
            "Session_ID": "SYN-S2",
            "Date": "2031-02-05",
            "Session_Dialogue": {
                "dialogue_turn_1": [
                    {"role": "user", "content": SHARED_TEXT},
                    {"role": "assistant", "content": "The wheel room is repainted every second summer."},
                ],
            },
            "Session_Questions": [
                {"question_id": "SYN-Q2", "question": "How often is the kiln fired?"},
                {"question_id": "SYN-Q3", "question": "What happens to the wheel room?"},
            ],
        },
        {
            "Session_ID": "SYN-S3",
            "Date": "2031-03-05",
            "Session_Dialogue": {
                "dialogue_turn_1": [
                    {"role": "user", "content": "Slip trailing needs a finer nozzle than the annexe owns."},
                ],
            },
            "Session_Questions": [
                {"question_id": "SYN-Q4", "question": "What tool is missing for slip trailing?"},
            ],
        },
    ],
}


def prove_future_guard(leaf: dict) -> dict:
    """Show the chronology guard fires, and say honestly where it can fire.

    The runner's inline check compares each mapped return's session index with
    the question's. In a correct in-order run the ledger cannot yet hold a
    future session, so that check is a backstop rather than something a stub can
    trip; a stub returning "the newest id" returns a *current* session and
    proves nothing. What can be exercised directly is the frozen contract
    function the boundary rests on, plus the count of returns the inline check
    actually inspected in this preflight.
    """
    from memory_bakeoff import memconflict as M

    question = M.Question(
        persona_id="SYN-PREFLIGHT", session_id="SYN-S1", session_index=0,
        question_id="SYN-Q1", text="Where are the glazes kept?",
    )
    past = M.Unit(persona_id="SYN-PREFLIGHT", session_id="SYN-S1", session_index=0,
                  turn_index=1, message_index=1, role="user", text="x", date="2031-01-05")
    future = M.Unit(persona_id="SYN-PREFLIGHT", session_id="SYN-S2", session_index=1,
                    turn_index=1, message_index=1, role="user", text="y", date="2031-02-05")

    M.assert_within_boundary(question, [past])
    try:
        M.assert_within_boundary(question, [past, future])
        raised, message = False, "a future-session unit was accepted"
    except ReportingError as exc:
        raised, message = True, str(exc)[:200]

    inspected = sum(len(record["returned"]) for record in leaf["questions"])
    mapped = sum(
        1
        for record in leaf["questions"]
        for item in record["returned"]
        if item["session_index"] is not None
    )
    within = all(
        item["session_index"] <= record["session_index"]
        for record in leaf["questions"]
        for item in record["returned"]
        if item["session_index"] is not None
    )
    return {
        "frozen_boundary_function_raises": raised,
        "message": message,
        "allowed_prefix_accepted": True,
        "returns_inspected_by_the_inline_check": inspected,
        "returns_with_a_mapped_session": mapped,
        "every_return_within_the_allowed_prefix": within,
        "note": (
            "an in-order run cannot place a future session in the ledger, so the inline "
            "check is a backstop; the boundary itself is proven on the frozen function"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/membukkit_memconflict_gen42_calibration"))
    ap.add_argument("--state-root", default="/private/tmp")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    root = Path(args.state_root) / f"membukkit-gen42-preflight-{int(time.time())}"
    root.mkdir(parents=True)

    checks: dict = {}

    # 1. adapter payload contract
    payload = ADAPTER.write_payload("a fact", 7)
    ADAPTER.assert_write_payload(payload)
    rejected = []
    for bad in ({"text": "x", "fact_id": "S1-turn2"}, {"text": "", "fact_id": "m000001"},
                {"text": "x", "fact_id": "m000001", "session_id": "S1"}):
        try:
            ADAPTER.assert_write_payload(bad)
            rejected.append({"payload": bad, "rejected": False})
        except ValueError:
            rejected.append({"payload": bad, "rejected": True})
    checks["adapter_payload"] = {
        "accepted": payload,
        "rejections": rejected,
        "all_bad_payloads_rejected": all(r["rejected"] for r in rejected),
    }

    # 2. the frozen procedure, end to end, on synthetic content
    G37.ADAPTERS["membukkit"] = ADAPTER
    G37.FROZEN_ADAPTER_SHA["membukkit"] = ADAPTER.adapter_contract_sha256()
    G37.E.ENGINES.update(G42.ENGINES)
    leaf, ledger = G37.run_persona("membukkit", SYNTHETIC_PERSONA, root)

    returned = [item for record in leaf["questions"] for item in record["returned"]]
    checks["end_to_end"] = {
        "messages_offered": leaf["operations"]["attempted_writes"],
        "successful_writes": leaf["operations"]["successful_writes"],
        "malformed_excluded": leaf["operations"]["malformed_excluded"],
        "distinct_native_ids": leaf["operations"]["distinct_native_ids"],
        "duplicate_message_texts": leaf["operations"]["duplicate_message_texts"],
        "native_id_replacements": leaf["operations"]["native_id_replacements"],
        "questions_executed": leaf["operations"]["questions_executed"],
        "inventory": leaf["inventory"],
        "unmapped_items": sum(1 for r in returned if r["provenance_status"] != "mapped"),
        "read_side_effect_audit": leaf["read_side_effect_audit"],
        "deterministic_repeats": leaf["deterministic_repeats"],
    }

    # 3. identical text under distinct receipts must stay two rows
    inv = leaf["inventory"]
    checks["duplicate_text_not_collapsed"] = {
        "shared_text_occurrences": 2,
        "rows": inv["rows"],
        "distinct_ids": inv["distinct_ids"],
        "distinct_texts": inv["distinct_texts"],
        "kept_both": inv["rows"] == leaf["operations"]["successful_writes"]
        and inv["distinct_texts"] < inv["rows"],
    }

    # 4. store isolation: a second universe starts empty and stays separate
    a = G42.MemBukkitEngine("SYN-ISO-A", root)
    a.write("Only universe A knows about the salt kiln.")
    b = G42.MemBukkitEngine("SYN-ISO-B", root)
    b_before = b.inventory()["backend_count"]
    b.write("Only universe B knows about the raku tongs.")
    a_hits, _ = a.search("salt kiln")
    b_hits, _ = b.search("salt kiln")
    checks["store_isolation"] = {
        "b_started_empty": b_before == 0,
        "a_rows": a.inventory()["rows"],
        "b_rows": b.inventory()["rows"],
        "a_returns": len(a_hits),
        "b_returns": len(b_hits),
        "no_cross_universe_ids": not ({h["native_id"] for h in a_hits} & {h["native_id"] for h in b_hits}),
    }

    # 5. reads do not mutate; repeats reported as three separate quantities
    digest_before = a.state_digest()
    first, _ = a.search("Where is the salt kiln?")
    again, _ = a.search("Where is the salt kiln?")
    checks["repeat_probe"] = {
        "selected_set_identical": {i["native_id"] for i in first} == {i["native_id"] for i in again},
        "returned_order_identical": [i["native_id"] for i in first] == [i["native_id"] for i in again],
        "numeric_scores_identical": [i["score"] for i in first] == [i["score"] for i in again],
        "state_digest_unchanged_by_reads": digest_before == a.state_digest(),
    }

    # 6. the LLM path is refused rather than merely unused
    try:
        a.system._llm_fn("anything")
        llm = {"refused": False}
    except AssertionError as exc:
        llm = {"refused": True, "message": str(exc)}
    checks["llm_refused"] = llm

    # 7. device and model identity
    checks["identity"] = {
        "device_proof": a.device_proof,
        "required_devices": G42.REQUIRED_DEVICES,
        "model_paths": {
            role: str(Path(CONFIGURATIONS["intended"][role]["local"]).resolve())
            for role in ("encoder", "reranker")
        },
        "native_top_k": G42.NATIVE_TOP_K,
    }

    # 8. native rank equivalence is enforced, not assumed
    checks["native_rank_equivalence"] = {
        "checked_per_query": True,
        "mechanism": "public surface id set must equal the observed relevance order's id set",
        "raises": G42.NativeRankMismatch.__name__,
    }

    a.close()
    b.close()

    # 9. the future-session guard actually fires
    checks["future_session_guard"] = prove_future_guard(leaf)

    checks["adapter"] = {
        "version": ADAPTER.ADAPTER_VERSION,
        "sha256": ADAPTER.adapter_contract_sha256(),
        "engine_module_sha256": G42.__file__ and __import__("hashlib").sha256(
            Path(G42.__file__).read_bytes()
        ).hexdigest(),
    }
    checks["benchmark_fixture_touched"] = False

    passed = (
        checks["adapter_payload"]["all_bad_payloads_rejected"]
        and checks["end_to_end"]["unmapped_items"] == 0
        and checks["duplicate_text_not_collapsed"]["kept_both"]
        and checks["store_isolation"]["b_started_empty"]
        and checks["store_isolation"]["no_cross_universe_ids"]
        and checks["repeat_probe"]["state_digest_unchanged_by_reads"]
        and checks["llm_refused"]["refused"]
        and checks["future_session_guard"]["frozen_boundary_function_raises"]
        and checks["future_session_guard"]["every_return_within_the_allowed_prefix"]
    )
    checks["passed"] = passed

    (out / "preflight.json").write_text(json.dumps(checks, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: v for k, v in checks.items() if k in ("passed", "adapter")}, indent=1, default=str))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
