import pytest
from valve.limits import opening_percent


def test_negative_clamped_to_zero():
    """Negative raw readings must report 0, not their absolute value."""
    assert opening_percent(-10) == 0


def test_negative_one_clamped_to_zero():
    """Raw reading of -1 should clamp to 0."""
    assert opening_percent(-1) == 0


def test_zero_is_unchanged():
    """Raw reading of 0 is within range and should be unchanged."""
    assert opening_percent(0) == 0


def test_max_is_unchanged():
    """Raw reading of 100 is within range and should be unchanged."""
    assert opening_percent(100) == 100


def test_just_below_max_is_unchanged():
    """Raw reading of 99 is within range and should be unchanged."""
    assert opening_percent(99) == 99


def test_just_above_max_is_clamped():
    """Raw reading of 101 should clamp to 100."""
    assert opening_percent(101) == 100


def test_very_large_positive_is_clamped():
    """Very large positive raw readings should clamp to 100."""
    assert opening_percent(10000) == 100


def test_very_large_negative_is_clamped():
    """Very large negative raw readings should clamp to 0."""
    assert opening_percent(-10000) == 0
