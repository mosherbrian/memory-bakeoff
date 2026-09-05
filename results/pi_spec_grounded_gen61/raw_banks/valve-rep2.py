from valve.limits import opening_percent


def test_negative_values_are_clamped_to_zero():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-10) == 0


def test_negative_values_are_clamped_to_zero_edge():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-1) == 0


def test_exact_lower_bound_is_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(0) == 0


def test_exact_upper_bound_is_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(100) == 100


def test_values_inside_range_are_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(50) == 50


def test_values_inside_range_are_unchanged_edge_low():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(1) == 1


def test_values_inside_range_are_unchanged_edge_high():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(99) == 99


def test_large_positive_values_are_clamped_to_one_hundred():
    """REQUIREMENT: A raw reading above 100 reports 100."""
    assert opening_percent(1000) == 100


def test_large_negative_values_are_clamped_to_zero():
    """REQUIREMENT: A raw reading below 0 reports 0."""
    assert opening_percent(-1000) == 0
