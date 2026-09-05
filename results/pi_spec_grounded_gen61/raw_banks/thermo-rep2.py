from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    # 100 C = 212.0 F, rounded to 1 decimal place
    result = to_fahrenheit(100)
    assert result == 212.0
    assert isinstance(result, float)
    # Verify it's not rounded to 2 decimal places (which would still be 212.0, so check differently)
    # Use a value that shows the difference between 1 and 2 decimal places
    # 0 C = 32.0 F, 37 C = 98.6 F
    result2 = to_fahrenheit(37)
    assert result2 == 98.6


def test_places_argument_rounds_correctly():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    # 36.6 C = 97.88 F, with places=2 should give 97.88
    assert to_fahrenheit(36.6, places=2) == 97.88
    # 36.6 C = 97.88 F, with places=1 should give 97.9 (nearest rounding)
    assert to_fahrenheit(36.6, places=1) == 97.9
    # 36.6 C = 97.88 F, with places=0 should give 98.0
    assert to_fahrenheit(36.6, places=0) == 98.0


def test_zero_celsius_conversion():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    # 0 C = 32 F
    assert to_fahrenheit(0, places=1) == 32.0
    assert to_fahrenheit(0, places=2) == 32.0


def test_negative_celsius_conversion():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    # -40 C = -40 F
    assert to_fahrenheit(-40, places=1) == -40.0
    # -10 C = 14 F
    assert to_fahrenheit(-10, places=1) == 14.0


def test_return_type_is_float():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(100)
    assert isinstance(result, float)
    result2 = to_fahrenheit(100, places=2)
    assert isinstance(result2, float)


def test_default_places_parameter():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    # Verify that calling without places argument uses 1 decimal place
    # 36.6 C = 97.88 F, rounded to 1 decimal place = 97.9
    result = to_fahrenheit(36.6)
    assert result == 97.9


def test_high_precision_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    # 98.6 C = 209.48 F
    assert to_fahrenheit(98.6, places=2) == 209.48
    # 98.6 C = 209.48 F, rounded to 3 decimal places = 209.48
    assert to_fahrenheit(98.6, places=3) == 209.48


def test_no_midpoint_case_handling_required():
    """REQUIREMENT: Rounding is ordinary nearest-value rounding; no midpoint case arises in this task."""
    # Test a value that would normally be a midpoint to ensure standard rounding is used
    # 100 C = 212.0 F, which is exact
    assert to_fahrenheit(100, places=1) == 212.0
    # 37.5 C = 99.5 F, exact
    assert to_fahrenheit(37.5, places=1) == 99.5
