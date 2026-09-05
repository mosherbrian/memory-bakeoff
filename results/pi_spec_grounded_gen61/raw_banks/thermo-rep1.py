from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    assert to_fahrenheit(100) == 212.0
    # Check that the default places=1 is actually used by verifying a value
    # that would differ if places=2 was used
    assert to_fahrenheit(36.6) == 97.9


def test_places_one_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(36.6, places=1) == 97.9
    assert to_fahrenheit(0, places=1) == 32.0
    assert to_fahrenheit(-40, places=1) == -40.0


def test_places_zero_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=0) == 212.0
    assert to_fahrenheit(36.6, places=0) == 98.0


def test_places_two_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=2) == 212.0
    assert to_fahrenheit(36.6, places=2) == 97.88


def test_places_three_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=3) == 212.0
    assert to_fahrenheit(36.6, places=3) == 97.88


def test_negative_temperatures():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(-40, places=1) == -40.0
    assert to_fahrenheit(-100, places=1) == -148.0
    assert to_fahrenheit(-273.15, places=1) == -459.7


def test_zero_celsius():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(0, places=1) == 32.0


def test_return_type_is_float():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert isinstance(to_fahrenheit(100), float)
    assert isinstance(to_fahrenheit(100, places=1), float)
