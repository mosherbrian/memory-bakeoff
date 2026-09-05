import pytest
from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """When places is not supplied, result is rounded to ONE decimal place."""
    # 0 C -> 32.0 F (exact, 1 decimal place should keep .0)
    assert to_fahrenheit(0) == 32.0
    # 37 C -> 98.6 F (exact, 1 decimal place)
    assert to_fahrenheit(37) == 98.6
    # 100 C -> 212.0 F (exact, 1 decimal place)
    assert to_fahrenheit(100) == 212.0


def test_places_zero():
    """places=0 should round to integer (0 decimal places)."""
    assert to_fahrenheit(100, places=0) == 212
    assert to_fahrenheit(36.6, places=0) == 98


def test_places_three():
    """places=3 should round to 3 decimal places."""
    # 0 C -> 32.0 F
    assert to_fahrenheit(0, places=3) == 32.0
    # 36.6 C -> 97.88 F
    assert to_fahrenheit(36.6, places=3) == 97.88


def test_negative_celsius():
    """Negative celsius values should be handled correctly."""
    # -40 C -> -40 F (exact)
    assert to_fahrenheit(-40) == -40.0
    # -40 C -> -40 F with places=2
    assert to_fahrenheit(-40, places=2) == -40.0
    # 0 C -> 32.0 F
    assert to_fahrenheit(0, places=1) == 32.0


def test_return_type():
    """Result should be a float."""
    assert isinstance(to_fahrenheit(100), float)
    assert isinstance(to_fahrenheit(100, places=2), float)


def test_exact_integer_result():
    """When result is exact integer, rounding to 1 decimal place should still give float."""
    result = to_fahrenheit(0)
    assert result == 32.0
    assert isinstance(result, float)


def test_places_one_with_non_trivial_decimal():
    """Test that places=1 actually truncates/rounds to 1 decimal place."""
    # 36.6 C -> 97.88 F, rounded to 1 decimal place -> 97.9
    assert to_fahrenheit(36.6, places=1) == 97.9


def test_places_two_with_non_trivial_decimal():
    """Test that places=2 keeps 2 decimal places."""
    # 36.6 C -> 97.88 F, rounded to 2 decimal places -> 97.88
    assert to_fahrenheit(36.6, places=2) == 97.88


def test_small_celsius_value():
    """Test with small celsius values."""
    # 0.1 C -> 32.18 F, rounded to 1 decimal -> 32.2
    assert to_fahrenheit(0.1, places=1) == 32.2
    # 0.1 C -> 32.18 F, rounded to 2 decimals -> 32.18
    assert to_fahrenheit(0.1, places=2) == 32.18


def test_large_celsius_value():
    """Test with large celsius values."""
    # 1000 C -> 1832.0 F
    assert to_fahrenheit(1000, places=1) == 1832.0
    # 1000 C -> 1832.0 F
    assert to_fahrenheit(1000, places=2) == 1832.0
