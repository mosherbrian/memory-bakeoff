from ledger.money import charge


def test_halfway_rounds_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("2.675") == "2.68"


def test_halfway_rounds_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-2.675") == "-2.68"


def test_negative_halfway_rounds_half_away_from_zero_positive_side():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("2.685") == "2.69"


def test_negative_halfway_rounds_half_away_from_zero_negative_side():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("-2.685") == "-2.69"


def test_returns_string_with_exactly_two_decimals():
    """REQUIREMENT: returns it rounded to two decimal places, also as a string with exactly two decimals. """
    assert charge("1.0") == "1.00"


def test_returns_string_with_exactly_two_decimals_zero():
    """REQUIREMENT: returns it rounded to two decimal places, also as a string with exactly two decimals. """
    assert charge("0.0") == "0.00"


def test_returns_string_with_exactly_two_decimals_just_two():
    """REQUIREMENT: returns it rounded to two decimal places, also as a string with exactly two decimals. """
    assert charge("1.23") == "1.23"


def test_rounds_up_at_halfway():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("1.005") == "1.01"


def test_rounds_down_at_halfway_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("-1.005") == "-1.01"


def test_no_rounding_needed():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals. """
    assert charge("1.234") == "1.23"


def test_no_rounding_needed_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals. """
    assert charge("-1.234") == "-1.23"


def test_rounds_up_when_third_decimal_five():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("0.005") == "0.01"


def test_rounds_down_when_third_decimal_less_than_five():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("0.004") == "0.00"


def test_rounds_up_when_third_decimal_more_than_five():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. """
    assert charge("0.006") == "0.01"
