"""Positive AND negative controls. A scorer that says HIT to everything reads as
a working scorer; four guards in this repo were wrong that way in one afternoon.
"""
import pytest
from memory_bakeoff.ordering_scorer import hit, normalise, numeric_tokens


@pytest.mark.parametrize("gold,answer", [
    ("four", "4"),                       # the class the pilot lost
    ("4", "four"),
    ("seven", "7"),
    ("Two", "two"),
    ("Yes.", "Yes"),
    ("$400,000", "$400,000"),
    ("$400,000", "400000"),
    ("25:50", "your best time is 25:50"),  # answer says more than the gold
    ("Three times a week.", "three times a week"),
    ("Premier Silver", "premier silver"),
])
def test_these_are_the_same_answer(gold, answer):
    assert hit(gold, answer)


@pytest.mark.parametrize("gold,answer", [
    ("$400,000", "$350,000"),            # the superseded value must NOT score
    ("Paris", "Hawaii"),
    ("five", "4"),
    ("5", "four"),
    ("Friday", "Thursday"),
    ("Yes", "No"),
    ("132 points", "124"),
    ("4 weeks", "3 weeks"),
    ("600", "500"),
    ("Ford F-150 pickup truck", "Ford Mustang Shelby GT350"),
])
def test_these_are_different_answers(gold, answer):
    assert not hit(gold, answer)


def test_empty_gold_is_never_a_hit():
    assert not hit("", "anything")
    assert not hit("   ", "anything")


def test_empty_answer_is_never_a_hit():
    assert not hit("Paris", "")


def test_the_scorer_can_fail():
    """The control that the controls need: this must not be a function that
    returns True. If this ever passes trivially the suite above proves nothing."""
    assert hit("Paris", "Paris") and not hit("Paris", "Hawaii")


def test_number_normalisation_is_symmetric():
    assert hit("nine", "9") and hit("9", "nine")


def test_thousands_separators_do_not_change_the_number():
    assert numeric_tokens("$400,000") == ["400000"]
    assert normalise("$400,000") == "400000"


def test_a_bare_substring_of_a_word_is_not_a_hit():
    """'one' inside 'money' must not score. The pilot's crude matcher would."""
    assert not hit("one", "I spent the money")
