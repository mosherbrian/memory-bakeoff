from thermo.convert import to_fahrenheit


def test_default_places_is_one():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    # 0 C -> 32.0 F. With places=1, should be 32.0
    assert to_fahrenheit(0) == 32.0
    # 10 C -> 50.0 F. With places=1, should be 50.0
    assert to_fahrenheit(10) == 50.0


def test_default_places_argument_not_specified():
    """REQUIREMENT: When the caller does not supply it, the result is rounded to ONE decimal place."""
    # Verify the default is indeed 1, not 2 (which was the old default)
    # 100 C -> 212.0 F. With places=1, should be 212.0
    assert to_fahrenheit(100) == 212.0
    # 36.6 C -> 97.88 F. With places=1, should be 97.9
    assert to_fahrenheit(36.6) == 97.9


def test_places_zero():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    assert to_fahrenheit(100, places=0) == 212


def test_places_three():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    # 100 C -> 212.0 F, so with 3 places it should be 212.0
    assert to_fahrenheit(100, places=3) == 212.0
    # 36.6 C -> 97.88 F, so with 3 places it should be 97.88
    assert to_fahrenheit(36.6, places=3) == 97.88


def test_negative_celsius():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    # -40 C -> -40.0 F
    assert to_fahrenheit(-40) == -40.0
    # -40 C -> -40.0 F with 2 places
    assert to_fahrenheit(-40, places=2) == -40.0


def test_freezing_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    # 0 C -> 32.0 F
    assert to_fahrenheit(0) == 32.0


def test_boiling_point():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    # 100 C -> 212.0 F
    assert to_fahrenheit(100) == 212.0


def test_body_temperature_default():
    """REQUIREMENT: to_fahrenheit(celsius, places=1) converts a temperature and rounds the result to a number of decimal places."""
    # 36.6 C -> 97.88 F, rounded to 1 place -> 97.9
    assert to_fahrenheit(36.6) == 97.9


def test_places_argument_is_int():
    """REQUIREMENT: The `places` argument says how many decimal places to keep."""
    # Verify that places is an integer type hint
    import inspect
    sig = inspect.signature(to_fahrenheit)
    places_param = sig.parameters['places']
    assert places_param.annotation == int
