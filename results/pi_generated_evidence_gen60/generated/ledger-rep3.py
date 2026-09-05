import pytest
from ledger.money import charge


def test_rounds_half_up_positive():
    """Half away from zero: 2.675 should round to 2.68"""
    assert charge("2.675") == "2.68"


def test_rounds_half_up_negative():
    """Half away from zero: -2.675 should round to -2.68"""
    assert charge("-2.675") == "-2.68"


def test_rounds_half_down_positive():
    """Half away from zero: 2.665 should round to 2.67"""
    assert charge("2.665") == "2.67"


def test_rounds_half_down_negative():
    """Half away from zero: -2.665 should round to -2.67"""
    assert charge("-2.665") == "-2.67"


def test_already_two_decimals():
    """Amounts with exactly two decimals should remain unchanged"""
    assert charge("3.50") == "3.50"
    assert charge("0.00") == "0.00"
    assert charge("-1.23") == "-1.23"


def test_one_decimal():
    """Amounts with one decimal should get a trailing zero"""
    assert charge("5.5") == "5.50"
    assert charge("-3.2") == "-3.20"


def test_no_decimal():
    """Amounts with no decimal point should get two trailing zeros"""
    assert charge("10") == "10.00"
    assert charge("-7") == "-7.00"


def test_three_decimals_rounding_down():
    """Three decimals where the third digit < 5 should round down"""
    assert charge("1.234") == "1.23"
    assert charge("-1.234") == "-1.23"


def test_three_decimals_rounding_up():
    """Three decimals where the third digit > 5 should round up"""
    assert charge("1.236") == "1.24"
    assert charge("-1.236") == "-1.24"


def test_four_decimals_halfway():
    """Four decimals exactly at the halfway point"""
    assert charge("1.2345") == "1.23"
    assert charge("-1.2345") == "-1.23"


def test_four_decimals_above_halfway():
    """Four decimals above the halfway point"""
    assert charge("1.2355") == "1.24"
    assert charge("-1.2355") == "-1.24"


def test_very_small_positive():
    """Very small positive amounts"""
    assert charge("0.001") == "0.00"
    assert charge("0.005") == "0.01"


def test_very_small_negative():
    """Very small negative amounts"""
    assert charge("-0.001") == "-0.00"
    assert charge("-0.005") == "-0.01"


def test_large_amount():
    """Large amounts should still round correctly"""
    assert charge("1234567.895") == "1234567.90"
    assert charge("-1234567.895") == "-1234567.90"


def test_zero():
    """Zero should return '0.00'"""
    assert charge("0") == "0.00"
    assert charge("0.0") == "0.00"
    assert charge("0.00") == "0.00"


def test_just_below_half():
    """Values just below a halfway point should round down"""
    assert charge("2.6749") == "2.67"
    assert charge("-2.6749") == "-2.67"


def test_just_above_half():
    """Values just above a halfway point should round up"""
    assert charge("2.6751") == "2.68"
    assert charge("-2.6751") == "-2.68"


def test_string_format_exactly_two_decimals():
    """Ensure the output always has exactly two decimal places"""
    result = charge("5")
    assert result == "5.00"
    assert len(result.split(".")[1]) == 2

    result = charge("-5")
    assert result == "-5.00"
    assert len(result.split(".")[1]) == 2


def test_string_format_no_trailing_zeros_removed():
    """Ensure trailing zeros are preserved"""
    assert charge("1.10") == "1.10"
    assert charge("1.100") == "1.10"
    assert charge("1.1000") == "1.10"
