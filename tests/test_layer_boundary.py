"""Gen87: the layer boundary as a check, not a sentence."""
from __future__ import annotations

import pathlib

import pytest

from memory_bakeoff import layer_boundary as lb
from memory_bakeoff.longitudinal import TargetKind

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_every_target_kind_is_assigned_a_layer():
    """A new kind must be placed deliberately, not default into a table."""
    assert {str(k) for k in TargetKind} == set(lb.ANSWERABLE_AT)


def test_the_two_reader_kinds_are_the_ones_gen83_and_gen84_identified():
    assert lb.READER_LAYER_KINDS == {"recommended_procedure", "negative_unknown"}


def test_reader_kinds_are_permanently_not_demonstrable_at_the_retrieval_layer():
    for kind in lb.READER_LAYER_KINDS:
        assert lb.retrieval_layer_status(kind) == lb.NOT_DEMONSTRABLE
    for kind in set(lb.ANSWERABLE_AT) - lb.READER_LAYER_KINDS:
        assert lb.retrieval_layer_status(kind) == "measurable"


def test_a_retrieval_table_carrying_a_reader_kind_fails():
    with pytest.raises(ValueError, match="reader/full-product"):
        lb.assert_no_layer_mixing(
            {"current_truth": 6, "recommended_procedure": 0}, layer=lb.RETRIEVAL_ONLY)
    with pytest.raises(ValueError, match="reader/full-product"):
        lb.assert_no_layer_mixing(
            {"negative_unknown": 0}, layer=lb.RETRIEVAL_ONLY)


def test_a_reader_table_carrying_a_retrieval_kind_fails():
    """Wrong in the other direction too - the reader ran on two cases only."""
    with pytest.raises(ValueError):
        lb.assert_no_layer_mixing(
            {"negative_unknown": 1, "current_truth": 1}, layer=lb.RETRIEVAL_PLUS_READER)


def test_clean_tables_of_either_layer_pass():
    lb.assert_no_layer_mixing({"current_truth": 6, "scope_truth": 6},
                              layer=lb.RETRIEVAL_ONLY)
    lb.assert_no_layer_mixing({"recommended_procedure": 470, "negative_unknown": 26},
                              layer=lb.RETRIEVAL_PLUS_READER)


def test_an_unknown_layer_name_is_rejected():
    with pytest.raises(ValueError, match="unknown layer"):
        lb.assert_no_layer_mixing({}, layer="whatever")


def test_causal_attribution_is_withheld_not_guessed():
    closure = lb.closure()
    assert closure["causal_attribution"].startswith("WITHHELD")
    assert closure["no_new_model_calls"] is True
    assert closure["no_engine_reruns"] is True


def test_the_closure_reports_no_engine_difference_where_ordering_did_not_survive():
    closure = lb.closure()
    assert closure["unknown_abstention"]["engine_difference"] == \
        "none; nothing distinguishes the engines here"
    assert "NOT reported as an engine difference" in \
        closure["procedure_adoption"]["engine_difference"]
    assert closure["procedure_adoption"]["failed_procedure_adoption"].startswith(
        "fired zero times")


def test_retrieval_only_main_is_not_amended_by_the_reader_work():
    closure = lb.closure()
    assert closure["retrieval_only_status"].startswith("unchanged")
    assert "own branch" in closure["branch_policy"]


