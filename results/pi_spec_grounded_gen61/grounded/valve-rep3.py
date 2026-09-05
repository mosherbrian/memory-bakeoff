from valve.limits import opening_percent

def test_negative_values_are_clamped_to_zero():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-1) == 0
    assert opening_percent(-100) == 0
    assert opening_percent(-1000) == 0

def test_zero_is_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(0) == 0

def test_upper_bound_is_inclusive():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(100) == 100

def test_boundary_at_upper_limit():
    """REQUIREMENT: A raw reading above 100 reports 100."""
    assert opening_percent(101) == 100
    assert opening_percent(200) == 100