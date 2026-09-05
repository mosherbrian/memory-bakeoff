import pytest
from valve.limits import opening_percent


class TestOpeningPercentClamping:
    """Tests for the opening_percent function clamping behavior."""

    def test_zero_is_unchanged(self):
        """Zero should remain zero."""
        assert opening_percent(0) == 0

    def test_negative_value_clamped_to_zero(self):
        """Negative raw readings must be clamped to 0, not made positive."""
        assert opening_percent(-1) == 0

    def test_negative_value_clamped_to_zero_large(self):
        """Large negative raw readings must be clamped to 0."""
        assert opening_percent(-100) == 0

    def test_negative_value_clamped_to_zero_extreme(self):
        """Extreme negative raw readings must be clamped to 0."""
        assert opening_percent(-1000) == 0

    def test_upper_bound_is_clamped(self):
        """Raw readings above 100 must be clamped to 100."""
        assert opening_percent(150) == 100

    def test_upper_bound_is_clamped_large(self):
        """Large raw readings above 100 must be clamped to 100."""
        assert opening_percent(1000) == 100

    def test_in_range_is_unchanged_low(self):
        """A reading already inside the range is reported unchanged."""
        assert opening_percent(0) == 0

    def test_in_range_is_unchanged_mid(self):
        """A reading already inside the range is reported unchanged."""
        assert opening_percent(40) == 40

    def test_in_range_is_unchanged_high(self):
        """A reading already inside the range is reported unchanged."""
        assert opening_percent(99) == 99

    def test_exact_upper_bound_is_unchanged(self):
        """Exact upper bound (100) should remain 100."""
        assert opening_percent(100) == 100

    def test_exact_lower_bound_is_unchanged(self):
        """Exact lower bound (0) should remain 0."""
        assert opening_percent(0) == 0

    def test_just_below_zero_clamped(self):
        """Value just below zero must be clamped to 0."""
        assert opening_percent(-1) == 0

    def test_just_above_one_hundred_clamped(self):
        """Value just above 100 must be clamped to 100."""
        assert opening_percent(101) == 100

    def test_return_type_is_int(self):
        """The return value should be an integer."""
        result = opening_percent(-50)
        assert isinstance(result, int)
        result = opening_percent(150)
        assert isinstance(result, int)
        result = opening_percent(50)
        assert isinstance(result, int)
