from thermo.convert import to_fahrenheit

def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    assert to_fahrenheit(100) == 212.0
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
from thermo.convert import to_fahrenheit

def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    result = to_fahrenheit(100)
    assert result == 212.0
    assert isinstance(result, float)
    result2 = to_fahrenheit(37)
    assert result2 == 98.6

def test_places_argument_rounds_correctly():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(36.6, places=2) == 97.88
    assert to_fahrenheit(36.6, places=1) == 97.9
    assert to_fahrenheit(36.6, places=0) == 98.0

def test_zero_celsius_conversion():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(0, places=1) == 32.0
    assert to_fahrenheit(0, places=2) == 32.0

def test_negative_celsius_conversion():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(-40, places=1) == -40.0
    assert to_fahrenheit(-10, places=1) == 14.0

def test_return_type_is_float():
    """REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature and rounds the result to a number of decimal places."""
    result = to_fahrenheit(100)
    assert isinstance(result, float)
    result2 = to_fahrenheit(100, places=2)
    assert isinstance(result2, float)

def test_default_places_parameter():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    result = to_fahrenheit(36.6)
    assert result == 97.9

def test_high_precision_rounding():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(98.6, places=2) == 209.48
    assert to_fahrenheit(98.6, places=3) == 209.48

def test_no_midpoint_case_handling_required():
    """REQUIREMENT: Rounding is ordinary nearest-value rounding; no midpoint case arises in this task."""
    assert to_fahrenheit(100, places=1) == 212.0
    assert to_fahrenheit(37.5, places=1) == 99.5
from thermo.convert import to_fahrenheit

def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    assert to_fahrenheit(0) == 32.0
    assert to_fahrenheit(10) == 50.0

def test_places_zero():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=0) == 212

def test_places_three():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=3) == 212.0
    assert to_fahrenheit(36.6, places=3) == 97.88

def test_negative_celsius():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(-40) == -40.0
    assert to_fahrenheit(-40, places=2) == -40.0

def test_freezing_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(0) == 32.0

def test_boiling_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(100) == 212.0

def test_body_temperature_default():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    assert to_fahrenheit(36.6) == 97.9

def test_places_argument_is_int():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    import inspect
    sig = inspect.signature(to_fahrenheit)
    places_param = sig.parameters['places']
    assert places_param.annotation == int