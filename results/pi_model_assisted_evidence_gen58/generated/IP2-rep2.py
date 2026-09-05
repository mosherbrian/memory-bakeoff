from ferry.schedule import next_sailing, SAILINGS, as_list


class TestNextSailing:
    def test_returns_none_when_no_later_sailing(self):
        """When there is no later sailing in the day, next_sailing should return None."""
        assert next_sailing("10:30") is None

    def test_returns_none_after_last_sailing(self):
        """When the input is after the last sailing, next_sailing should return None."""
        assert next_sailing("11:00") is None

    def test_returns_none_after_midday(self):
        """When the input is well after the last sailing, next_sailing should return None."""
        assert next_sailing("23:59") is None

    def test_returns_next_sailing_when_one_exists(self):
        """When there is a later sailing, next_sailing should return it."""
        assert next_sailing("06:30") == "07:30"
        assert next_sailing("07:30") == "09:00"
        assert next_sailing("09:00") == "10:30"

    def test_returns_first_sailing_when_input_before_first(self):
        """When the input is before the first sailing, next_sailing should return the first."""
        assert next_sailing("05:00") == "06:00"

    def test_returns_none_for_exact_last_sailing(self):
        """When the input is exactly the last sailing, next_sailing should return None."""
        assert next_sailing("10:30") is None

    def test_does_not_wrap_to_first_sailing(self):
        """next_sailing should not wrap around to the first sailing."""
        assert next_sailing("10:30") != "06:00"
        assert next_sailing("23:59") != "06:00"


class TestAsList:
    def test_returns_list_of_strings(self):
        """as_list should return a list of time strings."""
        result = as_list()
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_contains_12_00_sailing(self):
        """as_list should include the 12:00 sailing."""
        result = as_list()
        assert "12:00" in result

    def test_contains_original_sailings(self):
        """as_list should still contain the original sailings."""
        result = as_list()
        assert "06:00" in result
        assert "07:30" in result
        assert "09:00" in result
        assert "10:30" in result

    def test_as_list_does_not_return_none_values(self):
        """as_list should not contain None values."""
        result = as_list()
        assert None not in result

    def test_as_list_returns_plain_list_not_generator(self):
        """as_list should return a plain list, not a generator or other iterable."""
        result = as_list()
        assert type(result) == list


class TestSAILINGS:
    def test_sailings_includes_12_00(self):
        """SAILINGS should include 12:00."""
        assert "12:00" in SAILINGS

    def test_sailings_order_preserved(self):
        """SAILINGS should be in chronological order."""
        assert SAILINGS.index("06:00") < SAILINGS.index("07:30")
        assert SAILINGS.index("07:30") < SAILINGS.index("09:00")
        assert SAILINGS.index("09:00") < SAILINGS.index("10:30")
        assert SAILINGS.index("10:30") < SAILINGS.index("12:00")
