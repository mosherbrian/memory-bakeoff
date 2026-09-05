"""Gen97: the first interference run, and the guards that shaped it."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference as itf
from memory_bakeoff import round3_adapters as r3

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "interference_gen97"
ENGINES = ("perseus", "mem0", "agentmemory", "hindsight")


@pytest.fixture(scope="module")
def curves():
    return json.loads((OUT / "curves.json").read_text())["within_engine_curves"]


def test_every_engine_ran_all_levels_and_repetitions():
    for engine in ENGINES:
        rows = json.loads((OUT / f"{engine}.json").read_text())["rows"]
        assert len(rows) == len(itf.LOAD_LEVELS) * 3
        assert {r["load"] for r in rows} == set(itf.LOAD_LEVELS)


def test_no_hit_was_left_unmapped():
    """The first hindsight attempt failed here; it must never pass silently."""
    for engine in ENGINES:
        rows = json.loads((OUT / f"{engine}.json").read_text())["rows"]
        for row in rows:
            if row.get("raw_returned"):
                assert row["returned"], (engine, row["load"])


def test_mechanisms_are_stable_across_repetitions(curves):
    for engine, entry in curves.items():
        for point in entry["curve"]:
            assert point["mechanisms_stable_across_repetitions"], (engine, point["load"])


def test_only_perseus_loses_the_target(curves):
    lost = {engine for engine, entry in curves.items()
            for point in entry["curve"] if not point["target_present"]}
    assert lost == {"perseus"}
    top = curves["perseus"]["curve"][-1]
    assert top["load"] == 64
    assert itf.DISTRACTOR_DISPLACEMENT in top["mechanisms"]


def test_perseus_rank_degrades_with_load(curves):
    ranks = [p["expected_rank"] for p in curves["perseus"]["curve"]]
    assert ranks[0] == [2]
    assert ranks[1] == [3, 4], "rank varies across repetitions at load 4"
    assert ranks[2] == [5]
    assert ranks[3] == [None]


def test_mem0_and_hindsight_hold_rank_two_throughout(curves):
    for engine in ("mem0", "hindsight"):
        for point in curves[engine]["curve"]:
            assert point["target_present"] and point["expected_rank"] == [2], engine


def test_agentmemory_ranks_the_current_fact_first_throughout(curves):
    for point in curves["agentmemory"]["curve"]:
        assert point["expected_rank"] == [1]
        assert itf.RETRIEVAL_WINDOW_EFFECT in point["mechanisms"]


def test_hindsight_volume_grows_with_load(curves):
    counts = [p["returned_count"][0] for p in curves["hindsight"]["curve"]]
    assert counts == [2, 6, 18, 66]
    assert curves["hindsight"]["window_expressible"] is False


def test_stale_interference_is_universal(curves):
    for engine, entry in curves.items():
        for point in entry["curve"]:
            assert itf.STALE_VERSION_INTERFERENCE in point["mechanisms"], engine


def test_cross_scope_contamination_never_occurred(curves):
    for engine, entry in curves.items():
        for point in entry["curve"]:
            assert itf.CROSS_SCOPE_CONTAMINATION not in point["mechanisms"], engine


def test_hindsight_attribution_is_not_inferred():
    payload = json.loads((OUT / "hindsight.json").read_text())
    assert payload["saturation"]["saturated_is"] == r3.NOT_DEMONSTRABLE
    for row in payload["rows"]:
        assert row["window_saturated"] is None
        assert row["window_expressible"] is False
        assert itf.TRUE_FORGETTING not in row["mechanisms"]
        assert itf.DISTRACTOR_DISPLACEMENT not in row["mechanisms"]


def test_the_summary_carries_no_cross_engine_total():
    payload = json.loads((OUT / "curves.json").read_text())
    r3.assert_within_engine_only(payload)
    itf.assert_no_pooled_accuracy(json.dumps(payload["why_no_shared_total"]))
    assert "not the same quantity" in payload["why_no_shared_total"]
