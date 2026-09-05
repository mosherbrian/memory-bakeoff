from thermo.convert import to_fahrenheit

def test_default_places_is_one():
    """
    REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place.
    """
    assert to_fahrenheit(100) == 212.0
    assert to_fahrenheit(36.6) == 97.9

def test_places_argument_specified_as_one():
    """
    REQUIREMENT: The `places` argument says how many decimal places to keep.
    """
    assert to_fahrenheit(36.6, places=1) == 97.9

def test_places_argument_specified_as_two():
    """
    REQUIREMENT: The `places` argument says how many decimal places to keep.
    """
    assert to_fahrenheit(36.6, places=2) == 97.88

def test_places_argument_specified_as_zero():
    """
    REQUIREMENT: The `places` argument says how many decimal places to keep.
    """
    assert to_fahrenheit(100, places=0) == 212.0

def test_conversion_formula_correctness():
    """
    REQUIREMENT: `to_fahrenheit(celsius, places=1)` converts a temperature
    """
    assert to_fahrenheit(0, places=1) == 32.0
    assert to_fahrenheit(-40, places=1) == -40.0
    assert to_fahrenheit(37, places=1) == 98.6

def test_no_midpoint_case_arises():
    """
    REQUIREMENT: Rounding is ordinary nearest-value rounding; no midpoint case arises in this task.
    """
    assert to_fahrenheit(100.005, places=2) == 212.01