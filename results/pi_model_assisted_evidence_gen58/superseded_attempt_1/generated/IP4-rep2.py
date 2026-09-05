from lockgate.valve import clamp


def test_clamp_negative_to_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0


def test_clamp_negative_large_to_zero():
    """Large negative values should be clamped to zero."""
    assert clamp(-100) == 0


def test_clamp_negative_float_like_to_zero():
    """Negative values (even small ones) should be clamped to zero."""
    assert clamp(-0) == 0


def test_clamp_zero_remains_zero():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_clamp_positive_small_remains_same():
    """Positive values below max should remain unchanged."""
    assert clamp(50) == 50


def test_clamp_max_remains_same():
    """Max value should remain unchanged."""
    assert clamp(100) == 100


def test_clamp_upper_bound_still_works():
    """Upper bound behavior should still work as before."""
    assert clamp(140) == 100


def test_clamp_just_above_max():
    """Value just above max should be clamped to max."""
    assert clamp(101) == 100
