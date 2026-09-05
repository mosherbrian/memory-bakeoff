from valve.limits import opening_percent

def test_negative_raw_reports_zero():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not
physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-1) == 0
    assert opening_percent(-100) == 0
    assert opening_percent(-9999) == 0

def test_zero_raw_is_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(0) == 0

def test_one_hundred_raw_is_unchanged():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(100) == 100

def test_boundary_values():
    """REQUIREMENT: The reading must be clamped to the range 0 to 100 inclusive."""
    assert opening_percent(0) == 0
    assert opening_percent(100) == 100

def test_large_negative_values():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not
physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-1000) == 0

def test_large_positive_values():
    """REQUIREMENT: A raw reading above 100 reports 100."""
    assert opening_percent(101) == 100
    assert opening_percent(1000) == 100
    assert opening_percent(999999) == 100

def test_return_type_is_int():
    """REQUIREMENT: opening_percent(raw) reports a valve opening as a percentage."""
    assert isinstance(opening_percent(50), int)
    assert isinstance(opening_percent(-5), int)
    assert isinstance(opening_percent(150), int)