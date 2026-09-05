from ledger.money import charge


def test_halfway_positive_rounds_up():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("2.675") == "2.68"


def test_halfway_negative_rounds_away_from_zero():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-2.675") == "-2.68"


def test_halfway_positive_small_amount():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("0.005") == "0.01"


def test_halfway_negative_small_amount():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-0.005") == "-0.01"


def test_halfway_larger_negative_amount():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-10.555") == "-10.56"


def test_non_halfway_positive():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("1.234") == "1.23"


def test_non_halfway_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("-1.234") == "-1.23"


def test_non_halfway_positive_rounds_up():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("1.236") == "1.24"


def test_non_halfway_negative_rounds_up_magnitude():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("-1.236") == "-1.24"


def test_already_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("1.23") == "1.23"


def test_one_decimal():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("1.2") == "1.20"


def test_integer():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("1") == "1.00"


def test_zero():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("0") == "0.00"


def test_negative_zero():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("-0") == "-0.00"


def test_three_decimals_not_halfway():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("3.141") == "3.14"


def test_three_decimals_not_halfway_rounds_up():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("3.146") == "3.15"


def test_four_decimals_not_halfway():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("3.1411") == "3.14"


def test_four_decimals_not_halfway_rounds_up():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge("3.1461") == "3.15"


def test_result_has_exactly_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("1.2")
    assert "." in result
    assert len(result.split(".")[1]) == 2


def test_result_has_exactly_two_decimals_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge("-1.2")
    assert "." in result
    assert len(result.split(".")[1]) == 2


def test_halfway_edge_case_0_005():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge("0.005") == "0.01"


def test_halfway_edge_case_negative_0_005():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge("-0.005") == "-0.01"
