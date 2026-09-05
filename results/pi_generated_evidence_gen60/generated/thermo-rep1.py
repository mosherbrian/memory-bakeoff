from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """When places is not supplied, result is rounded to ONE decimal place."""
    # 100 C -> 212.0 F (exact, so 1 decimal place is 212.0)
    assert to_fahrenheit(100) == 212.0
    # 36.6 C -> 97.88 F, rounded to 1 decimal place -> 97.9
    assert to_fahrenheit(36.6) == 97.9


def test_places_zero():
    """places=0 should round to integer."""
    assert to_fahrenheit(36.6, places=0) == 98.0


def test_places_three():
    """places=3 should keep 3 decimal places."""
    # 0 C = 32.0 F exactly
    assert to_fahrenheit(0, places=3) == 32.0
    # 1 C = 33.8 F exactly
    assert to_fahrenheit(1, places=3) == 33.8
    # 10 C = 50.0 F exactly
    assert to_fahrenheit(10, places=3) == 50.0
    # 21.1 C = 69.98 F exactly
    assert to_fahrenheit(21.1, places=3) == 69.98


def test_negative_celsius():
    """Negative celsius values should be handled correctly."""
    # -40 C = -40 F exactly
    assert to_fahrenheit(-40, places=1) == -40.0
    # -10 C = 14.0 F exactly
    assert to_fahrenheit(-10, places=1) == 14.0


def test_zero_celsius():
    """0 C = 32 F."""
    assert to_fahrenheit(0, places=1) == 32.0


def test_body_temperature_default():
    """Body temperature 36.6 C with default places=1."""
    assert to_fahrenheit(36.6) == 97.9


def test_places_explicit_one():
    """places=1 should give same result as default."""
    assert to_fahrenheit(36.6, places=1) == 97.9
    assert to_fahrenheit(100, places=1) == 212.0


def test_large_celsius():
    """Large celsius values should work."""
    # 1000 C = 1832.0 F
    assert to_fahrenheit(1000, places=1) == 1832.0


def test_small_celsius():
    """Small celsius values should work."""
    # 0.1 C = 32.18 F, rounded to 1 decimal -> 32.2
    assert to_fahrenheit(0.1, places=1) == 32.2
