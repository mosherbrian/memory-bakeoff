import pytest
from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """When places is not supplied, the result should be rounded to 1 decimal place."""
    # 0 C -> 32.0 F (exact, but verify the default rounding behavior)
    assert to_fahrenheit(0) == 32.0
    # 10 C -> 50.0 F (exact)
    assert to_fahrenheit(10) == 50.0
    # 36.6 C -> 97.88 F, rounded to 1 decimal place should be 97.9
    assert to_fahrenheit(36.6) == 97.9


def test_places_zero():
    """places=0 should round to the nearest integer."""
    assert to_fahrenheit(36.6, places=0) == 98.0
    assert to_fahrenheit(0, places=0) == 32.0


def test_places_three():
    """places=3 should round to 3 decimal places."""
    # 100 C -> 212.0 F
    assert to_fahrenheit(100, places=3) == 212.0
    # 36.6 C -> 97.88 F
    assert to_fahrenheit(36.6, places=3) == 97.88


def test_negative_celsius():
    """Negative Celsius values should convert correctly."""
    # -40 C -> -40 F
    assert to_fahrenheit(-40) == -40.0
    # -40 C -> -40 F with explicit places
    assert to_fahrenheit(-40, places=2) == -40.0


def test_body_temperature_default():
    """37 C should round to 98.6 F with default places=1."""
    assert to_fahrenheit(37) == 98.6


def test_places_one_explicit():
    """Explicit places=1 should behave the same as default."""
    assert to_fahrenheit(36.6, places=1) == 97.9
    assert to_fahrenheit(37, places=1) == 98.6


def test_large_celsius():
    """Large Celsius values should convert correctly."""
    # 1000 C -> 1832.0 F
    assert to_fahrenheit(1000) == 1832.0
    assert to_fahrenheit(1000, places=2) == 1832.0


def test_small_celsius():
    """Small Celsius values should convert correctly."""
    # 0.1 C -> 32.18 F, rounded to 1 decimal place is 32.2
    assert to_fahrenheit(0.1) == 32.2
    assert to_fahrenheit(0.1, places=2) == 32.18


def test_type_returned_is_float():
    """The function should always return a float."""
    assert isinstance(to_fahrenheit(0), float)
    assert isinstance(to_fahrenheit(0, places=0), float)
    assert isinstance(to_fahrenheit(100, places=2), float)
