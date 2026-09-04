"""Gen42 focused tests: adapter contract, provenance, device, routing, digest."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.providers import membukkit_memconflict as ADAPTER  # noqa: E402

BASE = ROOT / "results" / "membukkit_memconflict_gen42_calibration"


def _json(name: str) -> dict:
    path = BASE / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


# --- adapter contract, no artifacts needed -----------------------------------


def test_receipts_are_opaque_ordinals():
    assert ADAPTER.receipt_for(1) == "m000001"
    assert ADAPTER.receipt_for(14304) == "m014304"


def test_only_text_and_receipt_reach_the_product():
    payload = ADAPTER.write_payload("released content", 3)
    assert set(payload) == {"text", "fact_id"}
    assert payload["text"] == "released content"
    ADAPTER.assert_write_payload(payload)


@pytest.mark.parametrize(
    "bad",
    [
        {"text": "x", "fact_id": "S1-turn2"},          # an identifier, not an ordinal
        {"text": "", "fact_id": "m000001"},            # empty indexed text
        {"text": "x", "fact_id": "m000001", "session_id": "S1"},  # a scorer-side field
        {"text": "x", "fact_id": "m000001", "conflict_type": "static"},
    ],
)
def test_payloads_outside_the_contract_are_rejected(bad):
    with pytest.raises(ValueError):
        ADAPTER.assert_write_payload(bad)


def test_adapter_hash_is_stable_and_self_describing():
    assert ADAPTER.adapter_contract_sha256() == hashlib.sha256(
        Path(ADAPTER.__file__).read_bytes()
    ).hexdigest()


# --- artifact-backed ---------------------------------------------------------


def test_preflight_passed_before_any_calibration_question():
    pre = _json("preflight.json")
    assert pre["passed"] is True
    assert pre["benchmark_fixture_touched"] is False
    assert pre["duplicate_text_not_collapsed"]["kept_both"] is True
    assert pre["store_isolation"]["no_cross_universe_ids"] is True
    assert pre["repeat_probe"]["state_digest_unchanged_by_reads"] is True
    assert pre["llm_refused"]["refused"] is True
    assert pre["future_session_guard"]["frozen_boundary_function_raises"] is True


def test_the_run_used_the_adapter_the_preflight_froze():
    pre, identity = _json("preflight.json"), _json("identity.json")
    assert pre["adapter"]["sha256"] == identity["preflight"]["adapter_sha256"]
    assert identity["adapter_version"] == ADAPTER.ADAPTER_VERSION


def test_models_were_pinned_and_on_the_frozen_device():
    identity = _json("identity.json")
    for proof in identity["device_proof"]:
        assert proof["devices"] == ["mps:0"]
        assert "/.membukkit/models/MemseekAI__" in proof["target"]
    assert identity["native_top_k"] == 5
    assert identity["retrieval"]["union_lanes"] == ["atomic"]
    assert identity["development_exposed"] is True


def test_exactly_the_frozen_calibration_personas_ran():
    identity = _json("identity.json")
    manifest = json.loads(
        (ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text()
    )
    assert sorted(identity["calibration_persona_ids"]) == sorted(manifest["calibration_persona_ids"])
    leaves = sorted(BASE.glob("persona-*.json"))
    if not leaves:
        pytest.skip("no Gen42 leaves in this checkout")
    assert len(leaves) == manifest["calibration_persona_count"]


def test_provenance_is_exact_and_nothing_leaked():
    report = _json("calibration-report.json")
    health = report["scored"]["retrieval_health"]
    assert health["unmapped_provenance_items"] == 0
    assert health["future_session_leakage"] == 0
    assert health["empty_returns"] == 0
    assert health["short_returns_under_5"] == 0
    assert report["operations"]["totals"]["write_failures"] == 0


def test_unmeasured_is_reported_not_zeroed():
    report = _json("calibration-report.json")
    overall = report["scored"]["overall"]
    assert overall["unmeasured_questions"] > 0
    assert overall["measured_questions"] + overall["unmeasured_questions"] == (
        report["operations"]["totals"]["questions_executed"]
    )


def test_routing_diagnostic_accounts_for_every_static_question():
    report = _json("calibration-report.json")
    route = report["routing_diagnostic"]
    counts = route["counts"]
    static = report["scored"]["by_conflict_type"]["static_conflict"]["measured_questions"]
    total = sum(counts.values())
    assert total == static
    assert route["gold_availability"]["gold_support_present_in_write_ledger"] == static
    shares = route["share_of_static_misses"]
    assert abs((shares["routing_exclusion"] or 0) + (shares["rank_loss"] or 0) - 1.0) < 1e-9


def test_determinism_is_three_quantities_not_one_boolean():
    det = _json("calibration-report.json")["determinism"]
    for key in ("returned_order_identical", "selected_set_identical", "numeric_scores_identical"):
        assert det[key] == det["repeat_probes"]


def test_scientific_digest_rebuilds_without_timing():
    import importlib

    sys.path.insert(0, str(ROOT / "scripts"))
    builder = importlib.import_module("build_membukkit_gen42_report")
    report = _json("calibration-report.json")
    recorded = report.pop("scientific_digest")
    rebuilt = hashlib.sha256(
        json.dumps(builder.strip(report), sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    assert rebuilt == recorded


def test_committed_calibration_context_is_read_not_recomputed():
    ctx = _json("calibration-report.json")["committed_calibration_context"]
    assert ctx["source"].endswith("exact-provenance-derived.json")
    for engine in ("perseus", "mem0"):
        assert ctx[engine]["measured_questions"] == 380


def test_earlier_generations_were_not_rewritten():
    gen37 = json.loads(
        (ROOT / "results/memconflict_gen37_calibration/exact-provenance-derived.json").read_text()
    )
    assert set(gen37["engines"]) == {"perseus", "mem0"}
    assert gen37["engines"]["perseus"]["overall"]["hit_at"]["3"]["rate"] == 0.4421
    gen8 = (ROOT / "research" / "MEMBUKKIT_FALLBACK_GEN8.md").read_text()
    assert "Post-Gen41 correction (2026-09-04)" in gen8
    assert "`torch` 2.13.0" in gen8  # the original runtime line is preserved, not deleted
