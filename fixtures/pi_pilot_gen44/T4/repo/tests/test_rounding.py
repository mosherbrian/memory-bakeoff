from tidewatch.rounding import clamp, normalise


def test_negative_readings_round_away_from_zero():
    assert normalise(-1.005) == -1.01


def test_clamp_bounds():
    assert clamp(3.0, 0.0, 2.0) == 2.0
