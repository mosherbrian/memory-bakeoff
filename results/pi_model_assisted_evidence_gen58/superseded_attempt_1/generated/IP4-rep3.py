from lockgate.valve import clamp, MAX_OPEN


def test_negative_opening_returns_zero():
    """Negative values must be clamped to zero."""
    assert clamp(-1) == 0
    assert clamp(-10) == 0
    assert clamp(-100) == 0


def test_zero_is_valid():
    """Zero is a valid opening and should remain zero."""
    assert clamp(0) == 0


def test_positive_below_max_is_unchanged():
    """Positive values below the max should remain unchanged."""
    assert clamp(1) == 1
    assert clamp(50) == 50
    assert clamp(MAX_OPEN - 1) == MAX_OPEN - 1


def test_negative_boundary():
    """Ensure the boundary between negative and zero is handled correctly."""
    assert clamp(-0.1) == 0  # Note: type hint is int, but let's check edge cases if possible
    # Since the type hint is int, we focus on integer inputs
    assert clamp(-1) == 0


def test_upper_bound_still_works():
    """Ensure the existing upper bound behavior is preserved."""
    assert clamp(MAX_OPEN) == MAX_OPEN
    assert clamp(MAX_OPEN + 1) == MAX_OPEN
    assert clamp(MAX_OPEN * 2) == MAX_OPEN
