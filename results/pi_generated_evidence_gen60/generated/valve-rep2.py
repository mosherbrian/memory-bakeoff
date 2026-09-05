from valve.limits import opening_percent


def test_negative_clamps_to_zero():
    """Negative raw readings must report 0, not a positive value."""
    assert opening_percent(-10) == 0


def test_zero_is_unchanged():
    """Zero is inside the range and should be reported unchanged."""
    assert opening_percent(0) == 0


def test_exact_upper_bound_is_unchanged():
    """100 is inside the range and should be reported unchanged."""
    assert opening_percent(100) == 100


def test_exact_lower_bound_is_unchanged():
    """0 is inside the range and should be reported unchanged."""
    assert opening_percent(0) == 0


def test_very_large_positive_clamps_to_100():
    """Very large positive raw readings must report 100."""
    assert opening_percent(10000) == 100


def test_very_large_negative_clamps_to_0():
    """Very large negative raw readings must report 0."""
    assert opening_percent(-10000) == 0


def test_one_below_upper_bound_is_unchanged():
    """99 is inside the range and should be reported unchanged."""
    assert opening_percent(99) == 99


def test_one_above_upper_bound_clamps_to_100():
    """101 is above the range and must report 100."""
    assert opening_percent(101) == 100


def test_one_below_lower_bound_clamps_to_0():
    """-1 is below the range and must report 0."""
    assert opening_percent(-1) == 0
