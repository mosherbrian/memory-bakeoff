import pytest
from ledger.money import charge


class TestChargeHalfAwayFromZero:
    """Tests for half-away-from-zero rounding behavior."""

    def test_positive_halfway_rounds_up(self):
        """2.675 is exactly halfway; should round to 2.68 (larger magnitude)."""
        assert charge("2.675") == "2.68"

    def test_negative_halfway_rounds_away_from_zero(self):
        """-2.675 is exactly halfway; should round to -2.68 (larger magnitude)."""
        assert charge("-2.675") == "-2.68"

    def test_positive_halfway_4_rounds_up(self):
        """2.125 should round to 2.13."""
        assert charge("2.125") == "2.13"

    def test_negative_halfway_4_rounds_away_from_zero(self):
        """-2.125 should round to -2.13."""
        assert charge("-2.125") == "-2.13"

    def test_positive_halfway_3_rounds_up(self):
        """1.005 should round to 1.01."""
        assert charge("1.005") == "1.01"

    def test_negative_halfway_3_rounds_away_from_zero(self):
        """-1.005 should round to -1.01."""
        assert charge("-1.005") == "-1.01"

    def test_halfway_at_boundary_995(self):
        """0.995 should round to 1.00."""
        assert charge("0.995") == "1.00"

    def test_negative_halfway_at_boundary_minus995(self):
        """-0.995 should round to -1.00."""
        assert charge("-0.995") == "-1.00"

    def test_halfway_with_more_decimals(self):
        """3.335 should round to 3.34."""
        assert charge("3.335") == "3.34"

    def test_negative_halfway_with_more_decimals(self):
        """-3.335 should round to -3.34."""
        assert charge("-3.335") == "-3.34"


class TestChargeNonHalfwayValues:
    """Tests for non-halfway values (should round normally)."""

    def test_positive_rounds_down(self):
        """2.344 should round to 2.34."""
        assert charge("2.344") == "2.34"

    def test_positive_rounds_up(self):
        """2.346 should round to 2.35."""
        assert charge("2.346") == "2.35"

    def test_negative_rounds_down_toward_zero(self):
        """-2.344 should round to -2.34."""
        assert charge("-2.344") == "-2.34"

    def test_negative_rounds_up_away_from_zero(self):
        """-2.346 should round to -2.35."""
        assert charge("-2.346") == "-2.35"

    def test_already_two_decimals(self):
        """2.50 should remain 2.50."""
        assert charge("2.50") == "2.50"

    def test_integer_string(self):
        """5 should become 5.00."""
        assert charge("5") == "5.00"

    def test_zero(self):
        """0 should become 0.00."""
        assert charge("0") == "0.00"

    def test_negative_zero(self):
        """-0 should become 0.00 or -0.00? Let's check standard behavior."""
        # -0.00 is technically valid but let's see what happens
        result = charge("-0")
        assert result in ("0.00", "-0.00")


class TestChargeOutputFormat:
    """Tests for output format requirements."""

    def test_exactly_two_decimal_places(self):
        """Output must always have exactly two decimal places."""
        assert charge("1") == "1.00"
        assert charge("1.1") == "1.10"
        assert charge("1.11") == "1.11"
        assert charge("1.111") == "1.11"

    def test_string_return_type(self):
        """Return value must be a string."""
        assert isinstance(charge("2.341"), str)

    def test_negative_sign_preserved(self):
        """Negative amounts should retain the negative sign."""
        assert charge("-5.55") == "-5.55"
        assert charge("-0.01") == "-0.01"


class TestChargeEdgeCases:
    """Edge cases that might trip up float-based implementations."""

    def test_2_675_not_float_issue(self):
        """
        The key test: 2.675 as a float is actually 2.6749999999999998...
        which would round to 2.67 with float rounding.
        But since we're given the string "2.675", it should round to 2.68.
        """
        assert charge("2.675") == "2.68"

    def test_1_005_not_float_issue(self):
        """
        1.005 as a float is 1.0049999999999999...
        which would round to 1.00 with float rounding.
        But as string "1.005", it should round to 1.01.
        """
        assert charge("1.005") == "1.01"

    def test_3_675_not_float_issue(self):
        """3.675 should round to 3.68, not 3.67."""
        assert charge("3.675") == "3.68"

    def test_4_675_not_float_issue(self):
        """4.675 should round to 4.68, not 4.67."""
        assert charge("4.675") == "4.68"

    def test_5_675_not_float_issue(self):
        """5.675 should round to 5.68, not 5.67."""
        assert charge("5.675") == "5.68"

    def test_6_675_not_float_issue(self):
        """6.675 should round to 6.68, not 6.67."""
        assert charge("6.675") == "6.68"

    def test_7_675_not_float_issue(self):
        """7.675 should round to 7.68, not 7.67."""
        assert charge("7.675") == "7.68"

    def test_8_675_not_float_issue(self):
        """8.675 should round to 8.68, not 8.67."""
        assert charge("8.675") == "8.68"

    def test_9_675_not_float_issue(self):
        """9.675 should round to 9.68, not 9.67."""
        assert charge("9.675") == "9.68"

    def test_large_amount(self):
        """Large amounts should still work correctly."""
        assert charge("1234567.895") == "1234567.90"

    def test_very_small_amount(self):
        """Very small amounts should work correctly."""
        assert charge("0.001") == "0.00"
        assert charge("0.005") == "0.01"
        assert charge("0.009") == "0.01"
