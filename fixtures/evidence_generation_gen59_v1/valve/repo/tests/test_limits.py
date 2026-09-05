from valve.limits import opening_percent


def test_upper_bound_is_clamped():
    assert opening_percent(150) == 100


def test_in_range_is_unchanged():
    assert opening_percent(40) == 40
