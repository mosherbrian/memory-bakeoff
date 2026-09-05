from ledger.money import charge


def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge("2.675") == "2.68"


def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge("-2.675") == "-2.68"


def test_half_away_from_zero_positive_edge():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge("0.005") == "0.01"


def test_half_away_from_zero_negative_edge():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge("-0.005") == "-0.01"


def test_returns_string_with_exactly_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("2.341")
    assert isinstance(result, str)
    assert len(result.split('.')[1]) == 2


def test_returns_string_with_exactly_two_decimals_zero_fraction():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("2.0")
    assert result == "2.00"


def test_returns_string_with_exactly_two_decimals_negative_zero_fraction():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("-2.0")
    assert result == "-2.00"


def test_halfway_positive_towards_larger_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge("1.005") == "1.01"


def test_halfway_negative_towards_larger_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge("-1.005") == "-1.01"


def test_halfway_larger_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge("9.995") == "10.00"


def test_halfway_larger_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge("-9.995") == "-10.00"


def test_no_float_conversion_accuracy_issue():
    """REQUIREMENT: Amounts are given as strings precisely so that a halfway value means what it says. Converting through a binary float loses that, because a value such as 2.675 is not stored exactly and can round the wrong way."""
    # This test ensures that 2.675 rounds to 2.68, not 2.67 (which would happen
    # if float conversion truncated the precision incorrectly)
    assert charge("2.675") == "2.68"
    assert charge("1.335") == "1.34"
    assert charge("1.345") == "1.35"
