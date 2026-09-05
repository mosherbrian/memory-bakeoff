from thermo.convert import to_fahrenheit


def test_conversion_with_explicit_places():
    assert to_fahrenheit(100, places=2) == 212.0
    assert to_fahrenheit(36.6, places=2) == 97.88
