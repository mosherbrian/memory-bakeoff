from lockgate.valve import clamp


def test_negative_clamped_to_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0


def test_negative_clamped_to_zero_large():
    """Large negative values should be clamped to zero."""
    assert clamp(-1000) == 0


def test_negative_clamped_to_zero_edge():
    """Value just below zero should be clamped to zero."""
    assert clamp(-0) == 0


def test_zero_is_not_clamped():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_positive_within_range_unchanged():
    """Positive values within range should remain unchanged."""
    assert clamp(50) == 50


def test_upper_bound_still_works():
    """Upper bound behavior should remain unchanged."""
    assert clamp(140) == 100


def test_upper_bound_exact():
    """Value exactly at upper bound should remain unchanged."""
    assert clamp(100) == 100


def test_upper_bound_one_below():
    """Value one below upper bound should remain unchanged."""
    assert clamp(99) == 99
