from thermo.convert import to_fahrenheit

def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    result = to_fahrenheit(0)
    assert result == 32.0
    assert round(result, 1) == result

def test_default_places_one_with_non_round_result():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    result = to_fahrenheit(37)
    assert result == 98.6

def test_places_zero():
    """REQUIREMENT: The places argument says how many decimal places to keep."""
    result = to_fahrenheit(100, places=0)
    assert result == 212.0

def test_places_three():
    """REQUIREMENT: The places argument says how many decimal places to keep."""
    result = to_fahrenheit(100, places=3)
    assert result == 212.0

def test_negative_celsius():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(-40, places=1)
    assert result == -40.0

def test_freezing_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(0, places=1)
    assert result == 32.0

def test_boiling_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(100, places=1)
    assert result == 212.0

def test_body_temperature_default():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(36.6)
    assert result == 97.9

def test_places_argument_is_int():
    """REQUIREMENT: The places argument says how many decimal places to keep."""
    result = to_fahrenheit(100, places=1)
    assert result == 212.0

def test_return_type_is_float():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(0, places=1)
    assert isinstance(result, float)