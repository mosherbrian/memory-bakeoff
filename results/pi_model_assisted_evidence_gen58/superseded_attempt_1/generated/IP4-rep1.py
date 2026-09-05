import pytest
from lockgate.valve import clamp, MAX_OPEN


def test_negative_values_return_zero():
    """Negative openings must be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_zero_is_unchanged():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_positive_values_below_max_unchanged():
    """Positive values below the max should remain unchanged."""
    assert clamp(1) == 1
    assert clamp(50) == 50
    assert clamp(MAX_OPEN - 1) == MAX_OPEN - 1


def test_max_value_is_unchanged():
    """The max value should remain unchanged."""
    assert clamp(MAX_OPEN) == MAX_OPEN


def test_upper_bound_still_works():
    """Existing upper bound behavior must be preserved."""
    assert clamp(140) == 100
    assert clamp(200) == 100
    assert clamp(MAX_OPEN + 1) == MAX_OPEN
