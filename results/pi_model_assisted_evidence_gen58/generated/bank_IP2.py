# --- IP2-rep1 ---
import pytest
from ferry.schedule import next_sailing, SAILINGS, as_list


class TestNextSailingRequirement:
    """Tests specifically for the task instruction:
    1. Add a 12:00 sailing.
    2. next_sailing returns None instead of wrapping when nothing later in the day.
    3. as_list returns a plain list of time strings (unchanged behavior but verify).
    """

    def test_r1_1200_sailing_exists(self):
        """Verify that 12:00 is in the SAILINGS list."""
        assert "12:00" in SAILINGS

    def test_r1_next_sailing_returns_none_when_no_later_sailing(self):
        """When after is the last sailing (12:00), next_sailing should return None, not wrap."""
        result = next_sailing("12:00")
        assert result is None

    def test_r1_next_sailing_returns_none_when_after_last_sailing(self):
        """When after is later than the last sailing, next_sailing should return None."""
        result = next_sailing("18:00")
        assert result is None

    def test_r1_next_sailing_does_not_wrap_to_first(self):
        """Ensure that next_sailing does NOT wrap around to the first sailing."""
        # If it wraps, it would return "06:00" instead of None
        result = next_sailing("12:00")
        assert result != "06:00", "next_sailing should not wrap to the first sailing"
        assert result is None

    def test_r1_next_sailing_still_works_for_existing_sailings(self):
        """Ensure existing next_sailing behavior is preserved for sailings before 12:00."""
        assert next_sailing("06:30") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"
        assert next_sailing("10:30") == "12:00"

    def test_r1_as_list_returns_plain_list_of_strings(self):
        """Verify as_list returns a plain list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_r1_as_list_contains_1200(self):
        """Verify as_list includes the new 12:00 sailing."""
        result = as_list()
        assert "12:00" in result

    def test_r1_as_list_contains_all_expected_sailings(self):
        """Verify as_list contains all expected sailings including 12:00."""
        result = as_list()
        expected = ["06:00", "07:30", "09:00", "10:30", "12:00"]
        assert result == expected

    def test_r1_as_list_does_not_return_tuple_or_other_type(self):
        """Ensure as_list does not return a tuple or other non-list type."""
        result = as_list()
        assert not isinstance(result, tuple)
        assert not isinstance(result, set)


# --- IP2-rep2 ---
from ferry.schedule import next_sailing, SAILINGS, as_list


class TestNextSailing:
    def test_r2_returns_none_when_no_later_sailing(self):
        """When there is no later sailing in the day, next_sailing should return None."""
        assert next_sailing("10:30") is None

    def test_r2_returns_none_after_last_sailing(self):
        """When the input is after the last sailing, next_sailing should return None."""
        assert next_sailing("11:00") is None

    def test_r2_returns_none_after_midday(self):
        """When the input is well after the last sailing, next_sailing should return None."""
        assert next_sailing("23:59") is None

    def test_r2_returns_next_sailing_when_one_exists(self):
        """When there is a later sailing, next_sailing should return it."""
        assert next_sailing("06:30") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"

    def test_r2_returns_first_sailing_when_input_before_first(self):
        """When the input is before the first sailing, next_sailing should return the first."""
        assert next_sailing("05:00") == "06:00"

    def test_r2_returns_none_for_exact_last_sailing(self):
        """When the input is exactly the last sailing, next_sailing should return None."""
        assert next_sailing("10:30") is None

    def test_r2_does_not_wrap_to_first_sailing(self):
        """next_sailing should not wrap around to the first sailing."""
        assert next_sailing("10:30") != "06:00"
        assert next_sailing("23:59") != "06:00"


class TestAsList:
    def test_r2_returns_list_of_strings(self):
        """as_list should return a list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_r2_contains_12_00_sailing(self):
        """as_list should include the 12:00 sailing."""
        result = as_list()
        assert "12:00" in result

    def test_r2_contains_original_sailings(self):
        """as_list should still contain the original sailings."""
        result = as_list()
        assert "06:00" in result
        assert "07:30" in result
        assert "09:00" in result
        assert "10:30" in result

    def test_r2_as_list_does_not_return_none_values(self):
        """as_list should not contain None values."""
        result = as_list()
        assert None not in result

    def test_r2_as_list_returns_plain_list_not_generator(self):
        """as_list should return a plain list, not a generator or other iterable."""
        result = as_list()
        assert type(result) == list


class TestSAILINGS:
    def test_r2_sailings_includes_12_00(self):
        """SAILINGS should include 12:00."""
        assert "12:00" in SAILINGS

    def test_r2_sailings_order_preserved(self):
        """SAILINGS should be in chronological order."""
        assert SAILINGS.index("06:00") < SAILINGS.index("07:30")
        assert SAILINGS.index("07:30") < SAILINGS.index("09:00")
        assert SAILINGS.index("09:00") < SAILINGS.index("10:30")
        assert SAILINGS.index("10:30") < SAILINGS.index("12:00")


# --- IP2-rep3 ---
import pytest
from ferry.schedule import next_sailing, as_list, SAILINGS


class TestNextSailing:
    """Tests for the next_sailing function."""

    def test_r3_returns_none_when_no_later_sailing(self):
        """When after is 12:00 or later, next_sailing should return None."""
        assert next_sailing("12:00") is None
        assert next_sailing("13:00") is None
        assert next_sailing("23:59") is None

    def test_r3_returns_none_after_last_sailing(self):
        """When after is after the last sailing, next_sailing should return None."""
        # The last sailing is now 12:00
        assert next_sailing("12:01") is None

    def test_r3_returns_correct_next_sailing(self):
        """When there is a later sailing, return the next one."""
        assert next_sailing("06:00") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"
        assert next_sailing("10:30") == "12:00"

    def test_r3_returns_first_sailing_for_early_times(self):
        """When after is before the first sailing, return the first sailing."""
        assert next_sailing("00:00") == "06:00"
        assert next_sailing("05:59") == "06:00"

    def test_r3_does_not_wrap_to_first_sailing(self):
        """next_sailing should NOT wrap around to the first sailing."""
        # This is the key behavior change: no wrapping
        assert next_sailing("12:00") is None
        assert next_sailing("11:00") == "12:00"
        # If it wrapped, next_sailing("12:00") would return "06:00"
        # We verify it returns None instead

    def test_r3_sailing_1200_exists(self):
        """Verify that 12:00 is in the SAILINGS list."""
        assert "12:00" in SAILINGS


class TestAsList:
    """Tests for the as_list function."""

    def test_r3_returns_list_of_time_strings(self):
        """as_list should return a plain list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_r3_as_list_includes_1200(self):
        """as_list should include 12:00."""
        result = as_list()
        assert "12:00" in result

    def test_r3_as_list_includes_original_sailings(self):
        """as_list should include all original sailings."""
        result = as_list()
        assert "06:00" in result
        assert "07:30" in result
        assert "09:00" in result
        assert "10:30" in result

    def test_r3_as_list_returns_copy(self):
        """as_list should return a new list, not the internal list."""
        result1 = as_list()
        result2 = as_list()
        assert result1 is not result2

    def test_r3_as_list_does_not_mutate_internal_state(self):
        """Modifying the returned list should not affect SAILINGS."""
        result = as_list()
        result.append("99:99")
        assert "99:99" not in SAILINGS
