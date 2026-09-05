import pytest
from ledger.money import charge


class TestChargeRounding:
    """Tests for charge() function."""

    def test_rounds_down_simple(self):
        """Amounts that round down normally."""
        assert charge("2.341") == "2.34"
        assert charge("7.812") == "7.81"
        assert charge("1.001") == "1.00"
        assert charge("0.001") == "0.00"

    def test_rounds_up_simple(self):
        """Amounts that round up normally."""
        assert charge("2.346") == "2.35"
        assert charge("7.817") == "7.82"
        assert charge("1.006") == "1.01"
        assert charge("0.006") == "0.01"

    def test_half_away_from_zero_positive(self):
        """Halfway values round away from zero for positive numbers."""
        # 2.675 is exactly halfway between 2.67 and 2.68
        assert charge("2.675") == "2.68"
        # 1.005 rounds to 1.01 (away from zero)
        assert charge("1.005") == "1.01"
        # 0.005 rounds to 0.01 (away from zero)
        assert charge("0.005") == "0.01"
        # 10.005 rounds to 10.01
        assert charge("10.005") == "10.01"
        # 99.995 rounds to 100.00
        assert charge("99.995") == "100.00"

    def test_half_away_from_zero_negative(self):
        """Halfway values round away from zero for negative numbers."""
        # -2.675 is exactly halfway between -2.67 and -2.68
        # "away from zero" means toward -2.68 (larger magnitude)
        assert charge("-2.675") == "-2.68"
        # -1.005 rounds to -1.01
        assert charge("-1.005") == "-1.01"
        # -0.005 rounds to -0.01
        assert charge("-0.005") == "-0.01"
        # -10.005 rounds to -10.01
        assert charge("-10.005") == "-10.01"
        # -99.995 rounds to -100.00
        assert charge("-99.995") == "-100.00"

    def test_already_two_decimals(self):
        """Amounts with exactly two decimal places are returned unchanged."""
        assert charge("2.50") == "2.50"
        assert charge("0.00") == "0.00"
        assert charge("-3.20") == "-3.20"
        assert charge("10.10") == "10.10"

    def test_one_decimal(self):
        """Amounts with one decimal place."""
        assert charge("2.5") == "2.50"
        assert charge("-3.2") == "-3.20"
        assert charge("0.1") == "0.10"

    def test_no_decimal(self):
        """Amounts with no decimal places."""
        assert charge("2") == "2.00"
        assert charge("0") == "0.00"
        assert charge("-5") == "-5.00"

    def test_three_decimals_not_halfway(self):
        """Three decimal places that are not halfway."""
        assert charge("2.674") == "2.67"
        assert charge("2.676") == "2.68"
        assert charge("-2.674") == "-2.67"
        assert charge("-2.676") == "-2.68"

    def test_four_or_more_decimals(self):
        """Amounts with more than two decimal places."""
        assert charge("2.6750") == "2.68"
        assert charge("2.67500") == "2.68"
        assert charge("1.2345") == "1.23"
        assert charge("1.2355") == "1.24"

    def test_large_amounts(self):
        """Large monetary amounts."""
        assert charge("1000.005") == "1000.01"
        assert charge("-1000.005") == "-1000.01"
        assert charge("999999.999") == "1000000.00"

    def test_very_small_amounts(self):
        """Very small monetary amounts."""
        assert charge("0.001") == "0.00"
        assert charge("0.004") == "0.00"
        assert charge("0.005") == "0.01"
        assert charge("0.009") == "0.01"

    def test_output_format_exactly_two_decimals(self):
        """Ensure output always has exactly two decimal places."""
        assert charge("1") == "1.00"
        assert charge("1.1") == "1.10"
        assert charge("1.12") == "1.12"
        assert charge("1.123") == "1.12"
        assert charge("0.00") == "0.00"
        assert charge("-0.00") == "-0.00"

    def test_string_type_returned(self):
        """Ensure the return value is a string."""
        result = charge("2.341")
        assert isinstance(result, str)

    def test_float_conversion_issue_halfway(self):
        """Verify that float conversion doesn't cause wrong rounding for halfway cases.
        
        This test ensures the implementation doesn't just use float() and round(),
        because float("2.675") != 2.675 exactly in binary floating point.
        """
        # If we convert 2.675 to float, it becomes slightly less than 2.675
        # due to binary representation, so round(float("2.675"), 2) gives "2.67"
        # but the correct answer is "2.68"
        assert charge("2.675") == "2.68"
        assert charge("1.005") == "1.01"
        assert charge("0.005") == "0.01"
        assert charge("1.125") == "1.13"
        assert charge("1.225") == "1.23"
        assert charge("1.325") == "1.33"
        assert charge("1.425") == "1.43"
        assert charge("1.525") == "1.53"
        assert charge("1.625") == "1.63"
        assert charge("1.725") == "1.73"
        assert charge("1.825") == "1.83"
        assert charge("1.925") == "1.93"

    def test_negative_halfway_cases(self):
        """Verify negative halfway values round away from zero correctly."""
        assert charge("-1.005") == "-1.01"
        assert charge("-1.105") == "-1.11"
        assert charge("-1.205") == "-1.21"
        assert charge("-1.305") == "-1.31"
        assert charge("-1.405") == "-1.41"
        assert charge("-1.505") == "-1.51"
        assert charge("-1.605") == "-1.61"
        assert charge("-1.705") == "-1.71"
        assert charge("-1.805") == "-1.81"
        assert charge("-1.905") == "-1.91"
