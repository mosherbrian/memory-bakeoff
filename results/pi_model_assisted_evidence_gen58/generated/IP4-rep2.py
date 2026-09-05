from lockgate.valve import clamp


def test_negative_opening_clamped_to_zero():
    """Negative values should be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_zero_is_not_clamped():
    """Zero should remain zero."""
    assert clamp(0) == 0


def test_positive_values_below_max_remain_unchanged():
    """Positive values below MAX_OPEN should remain unchanged."""
    assert clamp(1) == 1
    assert clamp(50) == 50
    assert clamp(99) == 99


def test_negative_and_positive_boundary():
    """Ensure the boundary between negative and non-negative is correct."""
    assert clamp(-0) == 0  # -0 is just 0 in Python
    assert clamp(0) == 0
    assert clamp(1) == 1


def test_upper_bound_still_works():
    """Ensure existing upper bound behavior is preserved."""
    assert clamp(140) == 100
    assert clamp(100) == 100
    assert clamp(200) == 100
