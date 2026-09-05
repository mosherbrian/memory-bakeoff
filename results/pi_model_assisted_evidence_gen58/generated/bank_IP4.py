# --- IP4-rep1 ---
from lockgate.valve import clamp


def test_r1_clamp_negative_returns_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_r1_clamp_zero_returns_zero():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_r1_clamp_positive_within_bounds_unchanged():
    """Positive values within bounds should remain unchanged."""
    assert clamp(50) == 50
    assert clamp(99) == 99


def test_r1_clamp_upper_bound_still_works():
    """Upper bound behavior should remain unchanged."""
    assert clamp(140) == 100
    assert clamp(100) == 100
    assert clamp(200) == 100


# --- IP4-rep2 ---
from lockgate.valve import clamp


def test_r2_negative_opening_clamped_to_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_r2_zero_is_not_clamped():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_r2_positive_values_below_max_remain_unchanged():
    """Positive values below MAX_OPEN should remain unchanged."""
    assert clamp(1) == 1
    assert clamp(50) == 50
    assert clamp(99) == 99


def test_r2_negative_and_positive_boundary():
    """Ensure the boundary between negative and non-negative is correct."""
    assert clamp(-0) == 0  # -0 is just 0 in Python
    assert clamp(0) == 0
    assert clamp(1) == 1


def test_r2_upper_bound_still_works():
    """Ensure existing upper bound behavior is preserved."""
    assert clamp(140) == 100
    assert clamp(100) == 100
    assert clamp(200) == 100


# --- IP4-rep3 ---
from lockgate.valve import clamp


def test_r3_negative_clamped_to_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0


def test_r3_negative_clamped_to_zero_large():
    """Large negative values should be clamped to zero."""
    assert clamp(-1000) == 0


def test_r3_negative_clamped_to_zero_edge():
    """Value just below zero should be clamped to zero."""
    assert clamp(-0) == 0


def test_r3_zero_is_not_clamped():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_r3_positive_within_range_unchanged():
    """Positive values within range should remain unchanged."""
    assert clamp(50) == 50


def test_r3_upper_bound_still_works():
    """Upper bound behavior should remain unchanged."""
    assert clamp(140) == 100


def test_r3_upper_bound_exact():
    """Value exactly at upper bound should remain unchanged."""
    assert clamp(100) == 100


def test_r3_upper_bound_one_below():
    """Value one below upper bound should remain unchanged."""
    assert clamp(99) == 99
