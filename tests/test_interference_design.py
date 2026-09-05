"""Gen95: the Round-3 interference ruler, proved before any product sees it."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference as itf

ROOT = pathlib.Path(__file__).resolve().parents[1]
RULER = ROOT / "results" / "interference_design_gen95" / "ruler.json"


@pytest.fixture(scope="module")
def fixture():
    return itf.build_fixture()


@pytest.fixture(scope="module")
def frozen():
    return json.loads(RULER.read_text())


# --- rule 1: reachability before any product ------------------------------
def test_every_mechanism_fires(fixture, frozen):
    control = itf.controls(fixture)
    fired = {m for entry in control.values() for m in entry["mechanisms"]}
    assert fired == set(itf.MECHANISMS)
    assert frozen["reachability"]["all_fired"] is True


def test_the_clean_control_is_silent(fixture):
    assert itf.controls(fixture)["clean"]["mechanisms"] == ()


def test_each_class_stays_silent_when_it_should(fixture):
    control = itf.controls(fixture)
    # rank matters: the window effect must not fire when the stale record leads
    assert control["window_effect_silent_when_stale_outranks"]["mechanisms"] == \
        (itf.STALE_VERSION_INTERFERENCE,)
    # saturation matters: displacement must not be charged with room to spare
    assert control["not_displacement_when_window_has_room"]["mechanisms"] == \
        (itf.TRUE_FORGETTING,)


def test_forgetting_and_displacement_are_actually_distinguished(fixture):
    """The pair a pooled count would merge. Same absence, different mechanism."""
    case = next(c for c in fixture.cases if c.load == 64)
    crowded = itf.score_case(fixture, case, ["D000", "D001", "D002", "D003", "D004"], 5)
    sparse = itf.score_case(fixture, case, ["D000"], 5)
    assert crowded["mechanisms"] == (itf.DISTRACTOR_DISPLACEMENT,)
    assert sparse["mechanisms"] == (itf.TRUE_FORGETTING,)
    assert crowded["window_saturated"] and not sparse["window_saturated"]


# --- rule 2: fair scope and configuration bindings from the start ---------
def test_every_observation_carries_a_scope_and_a_configuration(fixture):
    for observation in fixture.observations:
        assert observation.scope and observation.configuration


def test_the_foreign_record_differs_on_both_axes(fixture):
    foreign = fixture.by_id()["I002"]
    current = fixture.by_id()["I000"]
    assert foreign.scope != current.scope
    assert foreign.configuration != current.configuration
    assert itf.contract()["rules_carried_from_round_2"]["fair_bindings"]


def test_contamination_is_charged_only_for_a_foreign_record(fixture):
    case = fixture.cases[-1]
    assert itf.CROSS_SCOPE_CONTAMINATION in \
        itf.score_case(fixture, case, ["I000", "I002"], 5)["mechanisms"]
    assert itf.CROSS_SCOPE_CONTAMINATION not in \
        itf.score_case(fixture, case, ["I000", "D000"], 5)["mechanisms"]


# --- scale is the only independent variable ------------------------------
def test_every_level_is_generated_from_one_semantic_core(fixture):
    cores = {o.core for o in fixture.observations}
    assert cores == {itf.CORE["id"]}
    assert {c.query for c in fixture.cases} == {itf.CORE["query"]}
    assert {c.core for c in fixture.cases} == {itf.CORE["id"]}


def test_the_levels_differ_only_in_distractor_count(fixture):
    sizes = {c.load: len(itf.visible_ids(fixture, c)) for c in fixture.cases}
    assert sorted(sizes) == list(itf.LOAD_LEVELS)
    for load, size in sizes.items():
        assert size == load + 3, "core records plus exactly `load` distractors"


def test_distractors_share_the_subject_and_shape(fixture):
    for observation in fixture.observations:
        if observation.role == "distractor":
            assert itf.CORE["subject"] in observation.text
            assert "t/s" in observation.text


# --- rule 3: layers stay apart -------------------------------------------
def test_no_case_requires_abstention_or_a_judgement(fixture):
    for case in fixture.cases:
        assert case.expected, "a case passable only by returning nothing is a " \
                              "reader-layer question"


# --- rule 4: no pooled score ---------------------------------------------
def test_the_scorer_returns_mechanisms_not_a_mark(fixture):
    case = fixture.cases[-1]
    result = itf.score_case(fixture, case, ["I000"], 5)
    assert "mechanisms" in result and "score" not in result
    assert isinstance(result["mechanisms"], tuple)


def test_a_pooled_accuracy_summary_is_refused():
    for bad in ("accuracy at scale was 62%", "the overall accuracy is 0.6",
                "pooled score across levels", "mean accuracy per engine"):
        with pytest.raises(ValueError, match="before decomposition"):
            itf.assert_no_pooled_accuracy(bad)
    itf.assert_no_pooled_accuracy("displacement rises with load while forgetting "
                                  "stays flat")


# --- provenance and freezing ---------------------------------------------
def test_rank_and_provenance_are_preserved_per_case(fixture):
    case = fixture.cases[-1]
    result = itf.score_case(fixture, case, ["D000", "I000", "I001"], 5)
    assert result["ranks"] == {"D000": 1, "I000": 2, "I001": 3}
    assert result["expected_rank"] == 2
    assert result["distractors_returned"] == ["D000"]
    assert itf.contract()["per_case_rank_and_provenance_preserved"] is True


def test_the_fixture_is_frozen_with_a_hash(frozen):
    assert len(frozen["fixture_sha256"]) == 64
    assert len(frozen["contract_sha256"]) == 64
    assert frozen["contract"]["frozen_before_any_engine_run"] is True
    assert len(frozen["observations"]) == 67 and len(frozen["cases"]) == 4


def test_the_fixture_rebuilds_identically(fixture, frozen):
    assert [o.id for o in fixture.observations] == \
        [o["id"] for o in frozen["observations"]]
    assert [c.id for c in fixture.cases] == [c["id"] for c in frozen["cases"]]
