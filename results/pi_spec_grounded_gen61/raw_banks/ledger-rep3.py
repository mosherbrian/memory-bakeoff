from ledger.money import charge


def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("2.675") == "2.68"


def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-2.675") == "-2.68"


def test_half_away_from_zero_positive_other():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("1.005") == "1.01"


def test_half_away_from_zero_negative_other():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-1.005") == "-1.01"


def test_returns_string():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("2.341")
    assert isinstance(result, str)


def test_exact_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("2.341")
    assert "." in result
    assert len(result.split(".")[1]) == 2


def test_exact_two_decimals_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("-2.675")
    assert "." in result
    assert len(result.split(".")[1]) == 2


def test_exact_two_decimals_zero():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("0")
    assert result == "0.00"


def test_exact_two_decimals_zero_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("-0")
    assert result == "0.00"


def test_exact_two_decimals_zero_negative_sign():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("-0.0")
    assert result == "0.00"


def test_no_float_conversion_error_for_halfway():
    """REQUIREMENT: Amounts are given as strings precisely so that a halfway value means what it says. Converting through a binary float loses that, because a value such as 2.675 is not stored exactly and can round the wrong way."""
    assert charge("2.675") == "2.68"
    assert charge("1.005") == "1.01"
    assert charge("1.015") == "1.02"
    assert charge("1.025") == "1.03"
    assert charge("1.035") == "1.04"
    assert charge("1.045") == "1.05"
    assert charge("1.055") == "1.06"
    assert charge("1.065") == "1.07"
    assert charge("1.075") == "1.08"
    assert charge("1.085") == "1.09"
    assert charge("1.095") == "1.10"
