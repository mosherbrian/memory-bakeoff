#!/usr/bin/env python3
"""Gen37 preflight: prove both engines obey the frozen MemConflict contract.

Synthetic content only, with no MemConflict vocabulary. Every check is
fail-closed, and both adapter contracts are hashed here, before either engine
sees a calibration question.
"""
from __future__ import annotations

import argparse, hashlib, json, os, socket, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import memconflict as M
from memory_bakeoff import memconflict_engines as E
from memory_bakeoff.providers import mem0_memconflict as MEM0A
from memory_bakeoff.providers import perseus_memconflict as PERSA
from memory_bakeoff.round2_reporting import ReportingError

# Unrelated synthetic domain: rope, sails and tides. No persona, no conflict wording.
SYNTHETIC_A = [
    "The mainsail halyard was replaced with an eight millimetre polyester line.",
    "Tide tables show the harbour entrance shoals at low water springs.",
    "The chandlery on the north quay stocks stainless shackles in three sizes.",
    "A whipping twine repair on the jib sheet held for the whole season.",
]
SYNTHETIC_B = [
    "The allotment committee moved the water butt to the eastern fence.",
    "Runner beans were sown three weeks later than last year.",
]


def perseus_checks(root: Path) -> dict:
    checks: dict[str, object] = {}
    version = subprocess.run([str(E.PERSEUS_BIN), "--version"], text=True, capture_output=True).stdout.strip()
    checks["pinned_binary_identity"] = version == f"perseus-vault {PERSA.PINNED_VERSION} ({PERSA.PINNED_BUILD})"
    checks["binary_version_string"] = version

    engine_a = E.PerseusEngine("synthetic-A", root)
    engine_b = E.PerseusEngine("synthetic-B", root)
    ledger: dict[str, int] = {}
    try:
        for index, text in enumerate(SYNTHETIC_A):
            native_id, _ = engine_a.write(text)
            if native_id in ledger:
                raise ReportingError(f"duplicate native id from perseus: {native_id}")
            ledger[native_id] = index
        for text in SYNTHETIC_B:
            engine_b.write(text)

        checks["one_message_one_write"] = len(ledger) == len(SYNTHETIC_A)
        checks["write_count_matches_inventory"] = engine_a.inventory().get("active_entities") == len(SYNTHETIC_A)

        engine_a.open_read_snapshot()
        before = engine_a.state_digest()
        items, _ = engine_a.search("what line replaced the mainsail halyard")
        repeat, _ = engine_a.search("what line replaced the mainsail halyard")
        after = engine_a.state_digest()
        checks["reads_leave_state_unchanged"] = before == after
        checks["native_order_preserved"] = [i["rank"] for i in items] == list(range(1, len(items) + 1))
        checks["repeat_read_is_stable"] = [i["native_id"] for i in items] == [i["native_id"] for i in repeat]
        checks["every_hit_maps_through_ledger"] = all(i["native_id"] in ledger for i in items)
        checks["retrieval_is_non_empty"] = bool(items)

        engine_b.open_read_snapshot()
        cross, _ = engine_b.search("what line replaced the mainsail halyard")
        checks["persona_isolation"] = all(i["native_id"] not in ledger for i in cross)

        body = PERSA.body_for_message(SYNTHETIC_A[0])
        checks["no_identifier_in_indexed_body"] = True
        try:
            PERSA.assert_no_identifier_in_body(body, {"persona": "synthetic-A", "session": 3})
        except ValueError:
            checks["no_identifier_in_indexed_body"] = False
        leak_body = {"assertion": SYNTHETIC_A[0], "provenance": "synthetic-A|S3|T1"}
        try:
            PERSA.assert_no_identifier_in_body(leak_body, {"persona": "synthetic-A"})
            checks["identifier_leak_is_rejected"] = False
        except ValueError:
            checks["identifier_leak_is_rejected"] = True
    finally:
        engine_a.close()
        engine_b.close()
    return checks


def mem0_checks(root: Path) -> dict:
    checks: dict[str, object] = {}
    sys.path.insert(0, str(E.MEM0_CHECKOUT))
    import mem0

    checks["pinned_package_version"] = getattr(mem0, "__version__", None) == "2.0.19"
    checks["loaded_from_pinned_checkout"] = str(E.MEM0_CHECKOUT) in str(Path(mem0.__file__).resolve())

    # Embedded Qdrant allows one client per storage folder per process, so the
    # two personas are opened in sequence rather than together.
    engine_a = E.Mem0Engine("synthetic-A", root)
    ledger: dict[str, int] = {}
    try:
        for index, text in enumerate(SYNTHETIC_A):
            native_id, _ = engine_a.write(text)
            if native_id in ledger:
                raise ReportingError(f"duplicate native id from mem0: {native_id}")
            ledger[native_id] = index

        checks["one_message_one_write"] = len(ledger) == len(SYNTHETIC_A)
        checks["write_count_matches_inventory"] = engine_a.inventory().get("points") == len(SYNTHETIC_A)

        before = engine_a.state_digest()
        items, _ = engine_a.search("what line replaced the mainsail halyard")
        repeat, _ = engine_a.search("what line replaced the mainsail halyard")
        after = engine_a.state_digest()
        checks["reads_leave_state_unchanged"] = before == after
        checks["native_order_preserved"] = [i["rank"] for i in items] == list(range(1, len(items) + 1))
        checks["repeat_read_is_stable"] = [i["native_id"] for i in items] == [i["native_id"] for i in repeat]
        checks["every_hit_maps_through_ledger"] = all(i["native_id"] in ledger for i in items)
        checks["retrieval_is_non_empty"] = bool(items)

        stored = engine_a.memory.get_all(
            filters={"user_id": MEM0A.user_id_for_persona("synthetic-A")}, limit=1000)
        rows = stored.get("results") if isinstance(stored, dict) else stored
        checks["no_metadata_written"] = all(not (row.get("metadata") or {}) for row in (rows or []))
        checks["indexed_text_is_message_only"] = sorted(
            row.get("memory") for row in (rows or [])) == sorted(SYNTHETIC_A)
    finally:
        engine_a.close()

    engine_b = E.Mem0Engine("synthetic-B", root)
    try:
        for text in SYNTHETIC_B:
            engine_b.write(text)
        cross, _ = engine_b.search("what line replaced the mainsail halyard")
        checks["persona_isolation"] = all(i["native_id"] not in ledger for i in cross)
    finally:
        engine_b.close()
    return checks


def shared_checks() -> dict:
    checks: dict[str, object] = {}
    # the Gen36 guard must still reject every scorer-only field, recursively
    for payload in ({"content": "x", "answer": "gold"},
                    {"deep": {"conflict_type": "static_conflict"}},
                    {"units": [{"Session_Type": "update"}]},
                    {"a": {"b": {"Updated_Attributes": []}}}):
        try:
            M.assert_public_only(payload)
            checks["scorer_only_fields_rejected"] = False
            break
        except ReportingError:
            checks["scorer_only_fields_rejected"] = True

    persona = M.load_personas()[0]
    units = M.ingestion_units(persona)
    question = next(q for q in M.questions(persona) if q.session_index > 0)
    future = [u for u in units if u.session_index > question.session_index][:1]
    try:
        M.assert_within_boundary(question, future)
        checks["future_session_rejected"] = False
    except ReportingError:
        checks["future_session_rejected"] = True

    checks["contract_hash_unchanged"] = (
        M.contract_sha256() == "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28")
    checks["dataset_hash_unchanged"] = M.dataset_sha256() == M.DATASET_SHA256
    manifest = json.loads((ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text())
    checks["calibration_manifest_unchanged"] = (
        manifest["calibration_persona_ids"] == M.calibration_personas([p["ID"] for p in M.load_personas()]))
    checks["no_openai_key_in_environment"] = not os.environ.get("OPENAI_API_KEY")
    return checks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/memconflict_gen37_calibration/preflight.json"))
    args = ap.parse_args()

    root = Path(tempfile.mkdtemp(prefix="memconflict-gen37-preflight-", dir="/private/tmp"))
    findings = {
        "shared": shared_checks(),
        "perseus": perseus_checks(root),
        "mem0": mem0_checks(root),
        "adapter_contracts": {
            "perseus": {"version": PERSA.ADAPTER_VERSION, "sha256": PERSA.adapter_contract_sha256(),
                        "payload": PERSA.adapter_contract_payload()},
            "mem0": {"version": MEM0A.ADAPTER_VERSION, "sha256": MEM0A.adapter_contract_sha256(),
                     "payload": MEM0A.adapter_contract_payload()},
        },
        "state_dir": str(root),
    }
    booleans = {f"{group}.{name}": value
                for group in ("shared", "perseus", "mem0")
                for name, value in findings[group].items() if isinstance(value, bool)}
    findings["passed"] = all(booleans.values())

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(findings, indent=2, sort_keys=True) + "\n")
    for name, value in booleans.items():
        print(f"  {'PASS' if value else 'FAIL'}  {name}")
    print(f"perseus adapter {PERSA.adapter_contract_sha256()}")
    print(f"mem0 adapter    {MEM0A.adapter_contract_sha256()}")
    print(f"wrote {out}")
    if not findings["passed"]:
        raise SystemExit("gen37 product preflight failed; no calibration exposure may proceed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
