import pytest
from ferry.schedule import next_sailing, SAILINGS, as_list


class TestNextSailingRequirement:
    """Tests specifically for the task instruction:
    1. Add a 12:00 sailing.
    2. next_sailing returns None instead of wrapping when nothing later in the day.
    3. as_list returns a plain list of time strings (unchanged behavior but verify).
    """

    def test_1200_sailing_exists(self):
        """Verify that 12:00 is in the SAILINGS list."""
        assert "12:00" in SAILINGS

    def test_next_sailing_returns_none_when_no_later_sailing(self):
        """When after is the last sailing (12:00), next_sailing should return None, not wrap."""
        result = next_sailing("12:00")
        assert result is None

    def test_next_sailing_returns_none_when_after_last_sailing(self):
        """When after is later than the last sailing, next_sailing should return None."""
        result = next_sailing("18:00")
        assert result is None

    def test_next_sailing_does_not_wrap_to_first(self):
        """Ensure that next_sailing does NOT wrap around to the first sailing."""
        # If it wraps, it would return "06:00" instead of None
        result = next_sailing("12:00")
        assert result != "06:00", "next_sailing should not wrap to the first sailing"
        assert result is None

    def test_next_sailing_still_works_for_existing_sailings(self):
        """Ensure existing next_sailing behavior is preserved for sailings before 12:00."""
        assert next_sailing("06:30") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"
        assert next_sailing("10:30") == "12:00"

    def test_as_list_returns_plain_list_of_strings(self):
        """Verify as_list returns a plain list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_as_list_contains_1200(self):
        """Verify as_list includes the new 12:00 sailing."""
        result = as_list()
        assert "12:00" in result

    def test_as_list_contains_all_expected_sailings(self):
        """Verify as_list contains all expected sailings including 12:00."""
        result = as_list()
        expected = ["06:00", "07:30", "09:00", "10:30", "12:00"]
        assert result == expected

    def test_as_list_does_not_return_tuple_or_other_type(self):
        """Ensure as_list does not return a tuple or other non-list type."""
        result = as_list()
        assert not isinstance(result, tuple)
        assert not isinstance(result, set)
