"""Gen99: the replication verdicts, applied exactly as frozen in Gen98."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference as itf
from memory_bakeoff import interference_v2 as v2

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "replication_gen99"
ENGINES = ("perseus", "mem0", "agentmemory", "hindsight")


@pytest.fixture(scope="module")
def verdicts():
    return json.loads((OUT / "verdicts.json").read_text())


def test_every_engine_ran_every_core_load_and_repetition():
    for engine in ENGINES:
        rows = json.loads((OUT / f"{engine}.json").read_text())["rows"]
        assert len(rows) == 4 * len(itf.LOAD_LEVELS) * 3 == 48
        assert len({r["core"] for r in rows}) == 4


def test_no_hit_was_left_unmapped():
    for engine in ENGINES:
        for row in json.loads((OUT / f"{engine}.json").read_text())["rows"]:
            if row.get("raw_returned"):
                assert row["returned"], (engine, row["case"])
            assert row.get("unmapped", 0) == 0 or row["returned"]


def test_the_verdicts_used_the_frozen_contract(verdicts):
    assert verdicts["fixture_contract_sha256"] == v2.contract_sha256()
    assert set(verdicts["questions_as_frozen"]) == set(v2.REPLICATION_QUESTIONS)
    assert verdicts["questions_as_frozen"] == v2.REPLICATION_QUESTIONS


def test_q1_did_not_replicate(verdicts):
    q1 = verdicts["Q1_perseus_rank_declines_with_density"]
    assert q1["verdict"] == v2.FIXTURE_SPECIFIC
    assert q1["per_core"]["throughput:atlas"] is True
    assert sum(1 for v in q1["per_core"].values() if v) == 1


def test_perseus_keeps_the_target_in_the_other_three_cores(verdicts):
    curves = verdicts["per_core_curves"]["perseus"]
    for core in ("branch:vega", "oncall:kestrel", "budget:solstice"):
        assert all(p["target_present"] for p in curves[core]), core
    assert not curves["throughput:atlas"][-1]["target_present"]


def test_q2_replicated_across_every_core(verdicts):
    q2 = verdicts["Q2_stale_interference_recurs"]
    assert q2["verdict"] == v2.GENERAL
    assert all(q2["per_core"].values())


def test_stale_interference_appears_in_every_single_observation():
    total = 0
    for engine in ENGINES:
        for row in json.loads((OUT / f"{engine}.json").read_text())["rows"]:
            assert itf.STALE_VERSION_INTERFERENCE in row["mechanisms"], row["case"]
            total += 1
    assert total == 192


def test_q3_is_partial_for_all_three(verdicts):
    q3 = verdicts["Q3_other_engines_hold_their_shape"]
    assert set(q3) == {"mem0", "agentmemory", "hindsight"}
    held = {engine: sum(1 for v in entry["per_core"].values() if v)
            for engine, entry in q3.items()}
    for engine, entry in q3.items():
        assert entry["verdict"] == v2.PARTIAL, engine
    assert held == {"mem0": 3, "hindsight": 3, "agentmemory": 2}


def test_the_engines_fail_in_different_cores(verdicts):
    q3 = verdicts["Q3_other_engines_hold_their_shape"]
    failed = {engine: {core for core, held in entry["per_core"].items() if not held}
              for engine, entry in q3.items()}
    assert failed["mem0"] == {"branch:vega"}
    assert failed["hindsight"] == {"branch:vega"}
    assert failed["agentmemory"] == {"oncall:kestrel", "budget:solstice"}


def test_agentmemory_never_finds_the_target_in_kestrel(verdicts):
    """The finding only the replication could surface - and at zero load."""
    curve = verdicts["per_core_curves"]["agentmemory"]["oncall:kestrel"]
    assert all(not point["target_present"] for point in curve)
    rows = [r for r in json.loads((OUT / "agentmemory.json").read_text())["rows"]
            if r["core"] == "oncall:kestrel" and r["load"] == 0]
    for row in rows:
        assert itf.TRUE_FORGETTING in row["mechanisms"]
        assert row["window_saturated"] is False, "no distractors, window not full"
        assert row["unmapped"] == 0, "not a provenance defect"


def test_the_pooling_guard_still_catches_averaging():
    for bad in ("mean across cores", "pooled across cores", "core mean",
                "averaged across cores", "all cores combined"):
        with pytest.raises(ValueError, match="replication factor"):
            v2.assert_no_core_pooling(bad)
    v2.assert_no_core_pooling("interference appears across cores and loads")
