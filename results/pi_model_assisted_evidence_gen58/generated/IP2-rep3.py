import pytest
from ferry.schedule import next_sailing, as_list, SAILINGS


class TestNextSailing:
    """Tests for the next_sailing function."""

    def test_returns_none_when_no_later_sailing(self):
        """When after is 12:00 or later, next_sailing should return None."""
        assert next_sailing("12:00") is None
        assert next_sailing("13:00") is None
        assert next_sailing("23:59") is None

    def test_returns_none_after_last_sailing(self):
        """When after is after the last sailing, next_sailing should return None."""
        # The last sailing is now 12:00
        assert next_sailing("12:01") is None

    def test_returns_correct_next_sailing(self):
        """When there is a later sailing, return the next one."""
        assert next_sailing("06:00") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"
        assert next_sailing("10:30") == "12:00"

    def test_returns_first_sailing_for_early_times(self):
        """When after is before the first sailing, return the first sailing."""
        assert next_sailing("00:00") == "06:00"
        assert next_sailing("05:59") == "06:00"

    def test_does_not_wrap_to_first_sailing(self):
        """next_sailing should NOT wrap around to the first sailing."""
        # This is the key behavior change: no wrapping
        assert next_sailing("12:00") is None
        assert next_sailing("11:00") == "12:00"
        # If it wrapped, next_sailing("12:00") would return "06:00"
        # We verify it returns None instead

    def test_sailing_1200_exists(self):
        """Verify that 12:00 is in the SAILINGS list."""
        assert "12:00" in SAILINGS


class TestAsList:
    """Tests for the as_list function."""

    def test_returns_list_of_time_strings(self):
        """as_list should return a plain list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_as_list_includes_1200(self):
        """as_list should include 12:00."""
        result = as_list()
        assert "12:00" in result

    def test_as_list_includes_original_sailings(self):
        """as_list should include all original sailings."""
        result = as_list()
        assert "06:00" in result
        assert "07:30" in result
        assert "09:00" in result
        assert "10:30" in result

    def test_as_list_returns_copy(self):
        """as_list should return a new list, not the internal list."""
        result1 = as_list()
        result2 = as_list()
        assert result1 is not result2

    def test_as_list_does_not_mutate_internal_state(self):
        """Modifying the returned list should not affect SAILINGS."""
        result = as_list()
        result.append("99:99")
        assert "99:99" not in SAILINGS
