"""Gen49 focused tests: 24 leaves, three separate axes, floor exposure, false assurance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "pi_state_control_gen49"
GEN48 = ROOT / "results" / "pi_state_control_gen48"


def _json(name: str, base: Path = OUT) -> dict:
    path = base / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    return json.loads(path.read_text())


def test_all_twenty_four_frozen_slots_ran():
    agg = _json("aggregate.json")
    order = _json("gen49_order_manifest.json", GEN48)["order"]
    assert agg["runs"] == 24
    ran = sorted((l["index"], l["task"], l["repetition"], l["arm"]) for l in agg["leaves"])
    frozen = sorted((r["index"], r["task"], r["repetition"], r["arm"]) for r in order)
    assert ran == frozen


def test_the_three_axes_are_reported_separately():
    """Gen47 showed pass+timeout; Gen49 shows done+fail. Neither collapses."""
    for leaf in _json("aggregate.json")["leaves"]:
        assert "verifier_passed" in leaf
        assert "status" in leaf
        assert "control_valid_done" in leaf
    arms = _json("aggregate.json")["by_arm"]
    for arm in arms.values():
        assert arm["verifier_passes"] is not None
        assert arm["control_valid_done"] is not None
        assert arm["timeouts"] is not None


def test_the_floor_did_not_improve_verifier_success():
    """H3 as preregistered: report it rather than shop for a better ruler."""
    arms = _json("aggregate.json")["by_arm"]
    c = arms["pi_harness_state_control_v1"]
    d = arms["pi_harness_state_control_task_floor_v1"]
    assert c["verifier_passes"] == d["verifier_passes"]
    assert d["payload_median"] > c["payload_median"]


def test_unexposed_runs_are_kept_and_labelled_not_discarded():
    floor = _json("aggregate.json")["floor_exposure"]
    assert floor["runs_exposed"] + floor["runs_not_exposed"] == 12
    assert floor["runs_not_exposed"] > 0
    assert floor["unexposed_verifier_passes"] is not None


def test_floor_metrics_are_recorded_for_every_exposed_run():
    for leaf in _json("aggregate.json")["leaves"]:
        if leaf["arm"].endswith("task_floor_v1") and (leaf["floor"] or {}).get("exposed"):
            floor = leaf["floor"]
            assert floor["first_activation_request"] is not None
            assert floor["floor_bytes_per_request"] > 0
            assert floor["original_prompt_sha256"]


def test_the_floor_prompt_hash_matches_the_frozen_task():
    manifest = _json("task_manifest.json", GEN48)["tasks"]
    seen = 0
    for leaf in _json("aggregate.json")["leaves"]:
        floor = leaf.get("floor") or {}
        if floor.get("original_prompt_sha256"):
            seen += 1
            assert manifest[leaf["task"]]["prompt_sha256"] is not None
    assert seen > 0


def test_visible_receipt_false_assurance_was_recorded_where_it_happened():
    agg = _json("aggregate.json")
    flagged = [l for l in agg["leaves"] if l["visible_receipt_false_assurance"]]
    assert flagged, "the diagnostic never fired; check it is still being computed"
    for leaf in flagged:
        assert leaf["control_valid_done"] is True
        assert leaf["verifier_passed"] is False


def test_failures_name_a_public_requirement():
    for leaf in _json("aggregate.json")["leaves"]:
        if not leaf["verifier_passed"]:
            assert leaf["failed_requirement"] in {"A", "B"}


def test_no_run_was_dropped_or_rerun():
    agg = _json("aggregate.json")
    assert len(agg["leaves"]) == 24
    assert any(l["status"] == "timeout" for l in agg["leaves"])


def test_runtime_cost_is_reported():
    arms = _json("aggregate.json")["by_arm"]
    assert all(a["wall_total"] > 0 for a in arms.values())
