"""Gen38: a full-release number is only evidence if the pins, the gate, the
provenance chain and the resume rules all held for 20 hours."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from memory_bakeoff import memconflict as M
from memory_bakeoff.longitudinal import canonical_json
from memory_bakeoff.providers import mem0_memconflict as MEM0A
from memory_bakeoff.providers import perseus_memconflict as PERSA
from memory_bakeoff.round2_reporting import ReportingError

ROOT = Path(__file__).resolve().parents[1]
GEN36 = ROOT / "results/memconflict_gen36_contract"
GEN37 = ROOT / "results/memconflict_gen37_calibration"
GEN38 = ROOT / "results/memconflict_gen38_full_release"

FROZEN_ADAPTERS = {
    "perseus": "627f812d5296130cdee5062ee48a9690a8873e635ee5683c8dd51432fd0e2c99",
    "mem0": "920f496be7470fca3bb5da4fb26b6bde6b9a13214ba5b934d875b06e97e0d190",
}
EXPECTED_WRITES = 142093
EXPECTED_QUESTIONS = 3750

pytestmark = pytest.mark.skipif(not GEN38.is_dir(), reason="Gen38 evidence not present")


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "gen38runner", ROOT / "scripts/run_memconflict_gen38_full_release.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leaves_for(engine: str) -> list[dict]:
    directory = GEN38 / engine
    if not directory.is_dir():
        return []
    return [json.loads(p.read_text()) for p in sorted(directory.glob("persona-*.json"))]


def test_pins_are_unchanged():
    assert M.contract_sha256() == "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28"
    assert M.dataset_sha256() == M.DATASET_SHA256
    assert M.UPSTREAM_COMMIT == "ec51d5d36e87f7665d1337f3a88cbde95fc2a964"
    manifest = json.loads((GEN36 / "calibration-manifest.json").read_text())
    assert manifest["calibration_persona_ids"] == M.calibration_personas(
        [p["ID"] for p in M.load_personas()])


def test_adapters_are_byte_identical_to_gen37():
    assert PERSA.adapter_contract_sha256() == FROZEN_ADAPTERS["perseus"]
    assert MEM0A.adapter_contract_sha256() == FROZEN_ADAPTERS["mem0"]
    for engine in ("perseus", "mem0"):
        for leaf in leaves_for(engine):
            assert leaf["adapter_sha256"] == FROZEN_ADAPTERS[engine], leaf["persona_id"]


def test_heldout_is_exactly_release_minus_the_frozen_three():
    manifest = json.loads((GEN36 / "calibration-manifest.json").read_text())
    calibration = set(manifest["calibration_persona_ids"])
    everyone = {p["ID"] for p in M.load_personas()}
    assert len(calibration) == 3 and len(everyone) == 30
    assert len(everyone - calibration) == 27
    scientific = GEN38 / "scientific.json"
    if scientific.exists():
        slices = json.loads(scientific.read_text())["slices"]
        assert set(slices["primary_heldout_27"]) == everyone - calibration
        assert set(slices["calibration_3"]) == calibration


def test_release_totals_reconcile():
    personas = M.load_personas()
    assert sum(len(M.ingestion_units(p)) for p in personas) == EXPECTED_WRITES
    assert sum(len(M.questions(p)) for p in personas) == EXPECTED_QUESTIONS


def test_malformed_exclusion_list_is_unchanged():
    stats = json.loads((GEN36 / "dataset-stats.json").read_text())["dataset_statistics"]
    frozen = set(stats["malformed_message_ids"])
    observed = set()
    for persona in M.load_personas():
        for anomaly in M.dialogue_anomalies(persona):
            observed.add(f"{anomaly['persona_id']}|S{anomaly['session_id']}"
                         f"|T{anomaly['turn']}|M{anomaly['message']}")
    assert observed == frozen


def test_one_message_one_write_per_persona():
    personas = {p["ID"]: p for p in M.load_personas()}
    for engine in ("perseus", "mem0"):
        for leaf in leaves_for(engine):
            expected = len(M.ingestion_units(personas[leaf["persona_id"]]))
            ops = leaf["operations"]
            assert ops["expected_valid_messages"] == expected
            assert ops["successful_writes"] + len(ops["write_failures"]) == expected
            assert ops["distinct_native_ids"] == leaf["ledger_size"]


def test_every_returned_item_maps_and_respects_chronology():
    for engine in ("perseus", "mem0", "bm25"):
        for leaf in leaves_for(engine):
            for record in leaf["questions"]:
                for item in record["returned"]:
                    assert item["provenance_status"] == "mapped"
                    assert item["session_id"] is not None
                    assert item["session_index"] <= record["session_index"]
                ranks = [item["rank"] for item in record["returned"]]
                assert ranks == list(range(1, len(ranks) + 1))
                assert len(ranks) <= 5


def test_scorer_only_fields_still_cannot_reach_a_product():
    for payload in ({"text": "x", "answer": "gold"},
                    {"body": {"Session_Type": "update"}},
                    {"deep": {"conflict_type": "static_conflict"}}):
        with pytest.raises(ReportingError):
            M.assert_public_only(payload)


def test_conditional_unaddressable_questions_stay_unmeasured():
    scientific = GEN38 / "scientific.json"
    if not scientific.exists():
        pytest.skip("report not built yet")
    report = json.loads(scientific.read_text())
    for engine, result in report["engines"].items():
        conditional = result["secondary_full_30"]["by_conflict_type"].get("conditional_conflict")
        if conditional is None:
            continue
        # the frozen split is 263 addressable of 444 across the whole release
        assert conditional["unmeasured_questions"] > 0, engine
        for k in ("2", "3", "5"):
            assert conditional["hit_at"][k]["hits"] <= conditional["measured_questions"]


def test_mem0_inventory_is_never_a_get_all_page():
    for leaf in leaves_for("mem0"):
        inventory = leaf["inventory"]
        assert inventory.get("points") is None
        assert inventory.get("points_status") == "UNMEASURED"
    reconciliation = GEN38 / "inventory-reconciliation.json"
    if reconciliation.exists():
        payload = json.loads(reconciliation.read_text())
        for row in payload["reconciliation"].get("mem0", {}).values():
            assert row["native_evidence"]["source"].startswith("qdrant client.count")


def test_perseus_repeats_used_the_same_session_snapshot():
    for leaf in leaves_for("perseus"):
        for repeat in leaf["deterministic_repeats"]:
            assert repeat["snapshot"] == "same_session_boundary"
            assert repeat["same_session_order"] is True
            assert repeat["same_scores"] is True


def test_final_snapshot_repeat_design_is_rejected():
    """Regression for the Gen37 bug: a repeat compared against the end-of-run
    snapshot is a different store, and must not be accepted as a repeat."""
    leaf = {"deterministic_repeats": [{"question_key": "k", "same_session_order": False,
                                       "same_scores": True, "snapshot": "final_session"}]}
    bad = [r for r in leaf["deterministic_repeats"] if r["snapshot"] != "same_session_boundary"]
    assert bad, "a final-snapshot repeat must be detectable"
    with pytest.raises(AssertionError):
        for repeat in leaf["deterministic_repeats"]:
            assert repeat["snapshot"] == "same_session_boundary"


def test_repeat_set_selection_is_label_blind_and_deterministic():
    runner = load_runner()
    persona = M.load_personas()[0]
    keys = [q.key for q in M.questions(persona)]
    first = [k for k in keys if runner.stable_bucket(k, runner.REPEAT_MODULUS) == 0]
    second = [k for k in keys if runner.stable_bucket(k, runner.REPEAT_MODULUS) == 0]
    assert first == second
    assert all(isinstance(k, str) for k in first)


def test_resume_rejects_a_tampered_or_partial_leaf(tmp_path):
    runner = load_runner()
    persona = M.load_personas()[0]
    leaves = leaves_for("perseus")
    leaf = next((l for l in leaves if l["persona_id"] == persona["ID"]), None)
    if leaf is None:
        pytest.skip("that persona has not run yet")
    good = tmp_path / "good.json"
    good.write_text(json.dumps(leaf))
    assert runner.persona_is_complete(good, "perseus", persona)

    tampered = dict(leaf)
    tampered["questions"] = leaf["questions"][:-1]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(tampered))
    assert not runner.persona_is_complete(bad, "perseus", persona)

    wrong_digest = dict(leaf)
    wrong_digest["leaf_digest"] = "0" * 64
    other = tmp_path / "digest.json"
    other.write_text(json.dumps(wrong_digest))
    assert not runner.persona_is_complete(other, "perseus", persona)
    assert not runner.persona_is_complete(tmp_path / "absent.json", "perseus", persona)


def test_leaf_digest_excludes_timing_and_native_ids():
    runner = load_runner()
    leaves = leaves_for("perseus") or leaves_for("mem0")
    if not leaves:
        pytest.skip("no leaves yet")
    leaf = leaves[0]
    assert runner.leaf_digest(leaf) == leaf["leaf_digest"]
    noisier = json.loads(json.dumps(leaf))
    noisier["operations"]["wall_seconds"] = 999999.0
    noisier["operations"]["write_latency"] = {"p50_ms": 1}
    assert runner.leaf_digest(noisier) == leaf["leaf_digest"]


def test_replication_gate_recorded_its_declared_tolerance():
    gate = GEN38 / "calibration-replication.json"
    if not gate.exists():
        pytest.skip("gate has not run yet")
    payload = json.loads(gate.read_text())
    for engine, result in payload.items():
        assert result["tolerance"]["ordering_differences_must_be_tie_explained"] is True
        assert result["tie_instability"]["unexplained"] == 0, engine
        assert result["passed"] is True, engine


def test_bootstrap_contract_is_frozen():
    paired = GEN38 / "paired-analysis.json"
    if not paired.exists():
        pytest.skip("paired analysis not built yet")
    payload = json.loads(paired.read_text())
    interval = payload.get("persona_block_bootstrap") or {}
    if interval.get("status") == "UNMEASURED":
        pytest.skip("both engines not complete yet")
    assert interval["contract"]["seed"] == 20260903
    assert interval["contract"]["resamples"] == 10000
    assert interval["contract"]["unit"] == "persona"


def test_static_mechanism_diagnostic_is_scorer_side_only():
    diagnostic = GEN38 / "static-mechanism-diagnostic.json"
    if not diagnostic.exists():
        pytest.skip("diagnostic not built yet")
    payload = json.loads(diagnostic.read_text())
    for engine, row in payload.items():
        assert "top3_categories" in row["mechanism"]
        assert "static_hits" in row["admission"]
    source = (ROOT / "scripts/build_memconflict_gen38_report.py").read_text()
    # the report builder must never construct an engine or issue a query
    for forbidden in ("ENGINES[", "Memory.from_config", "open_read_snapshot", ".search("):
        assert forbidden not in source


def test_report_digest_is_deterministic_and_excludes_timing():
    scientific = GEN38 / "scientific.json"
    if not scientific.exists():
        pytest.skip("report not built yet")
    payload = json.loads(scientific.read_text())
    content = {k: v for k, v in payload.items() if k != "content_digest"}
    assert hashlib.sha256(canonical_json(content).encode()).hexdigest() == payload["content_digest"]
    assert (GEN38 / "content-digest.txt").read_text().strip() == payload["content_digest"]
    blob = canonical_json(content)
    for noisy in ("wall_seconds", "p50_ms", "latency_ms"):
        assert noisy not in blob


def test_no_reader_or_official_lane_was_used():
    scientific = GEN38 / "scientific.json"
    if not scientific.exists():
        pytest.skip("report not built yet")
    payload = json.loads(scientific.read_text())
    assert payload["lane"] == "memconflict-exact-whitebox-v1"
    assert payload["evidence_class"] == "external_benchmark_full_release_raw_product_exact_provenance"
    assert M.LANES["upstream_llm_judge"]["status_without_reader"] == "requires_reader_authorization"
