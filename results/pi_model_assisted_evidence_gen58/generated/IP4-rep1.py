from lockgate.valve import clamp


def test_clamp_negative_returns_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_clamp_zero_returns_zero():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_clamp_positive_within_bounds_unchanged():
    """Positive values within bounds should remain unchanged."""
    assert clamp(50) == 50
    assert clamp(99) == 99


def test_clamp_upper_bound_still_works():
    """Upper bound behavior should remain unchanged."""
    assert clamp(140) == 100
    assert clamp(100) == 100
    assert clamp(200) == 100
