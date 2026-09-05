from valve.limits import opening_percent

def test_negative_raw_reports_zero():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-10) == 0

def test_negative_raw_reports_zero_edge():
    """REQUIREMENT: A raw reading below 0 reports 0 — negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-1) == 0

def test_zero_raw_reports_zero():
    """REQUIREMENT: A reading already inside the range is reported unchanged."""
    assert opening_percent(0) == 0

def test_upper_bound_raw_reports_hundred():
    """REQUIREMENT: The reading must be clamped to the range 0 to 100 inclusive."""
    assert opening_percent(100) == 100

def test_very_large_raw_reports_hundred():
    """REQUIREMENT: A raw reading above 100 reports 100."""
    assert opening_percent(1000) == 100

def test_raw_below_zero_is_not_made_positive():
    """REQUIREMENT: negative openings are not physically meaningful and must not be passed through or made positive."""
    assert opening_percent(-50) == 0