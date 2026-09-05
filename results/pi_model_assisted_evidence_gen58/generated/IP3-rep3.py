import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Tests for ignoring items with missing or empty hold keys."""

    def test_ignores_missing_hold_key(self):
        """Items without a 'hold' key should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "B"},
            {"cargo": "widget"},  # no 'hold' key
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}
        assert "hold" not in result
        assert "" not in result

    def test_ignores_empty_hold_value(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}
        assert "" not in result

    def test_ignores_none_hold_value(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}
        assert None not in result

    def test_ignores_all_items_with_empty_holds(self):
        """When all items have empty holds, result should be empty dict."""
        items = [
            {"hold": ""},
            {"hold": ""},
        ]
        result = totals(items)
        assert result == {}

    def test_ignores_all_items_with_missing_holds(self):
        """When all items are missing hold key, result should be empty dict."""
        items = [
            {"cargo": "x"},
            {"cargo": "y"},
        ]
        result = totals(items)
        assert result == {}

    def test_valid_hold_not_affected(self):
        """Valid hold keys should still be counted correctly."""
        items = [
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "B"},
            {"hold": ""},
            {"hold": None},
        ]
        result = totals(items)
        assert result == {"A": 2, "B": 1}


class TestSummaryAlphabeticalOrder:
    """Tests for alphabetical ordering of holds in summary output."""

    def test_summary_sorted_alphabetically(self):
        """Holds should be listed in alphabetical order."""
        items = [
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=1, C=1"

    def test_summary_sorted_with_multiple_items_per_hold(self):
        """Sorting should work even when holds have multiple items."""
        items = [
            {"hold": "Z"},
            {"hold": "Z"},
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "M"},
        ]
        result = summary(items)
        assert result == "A=3, M=1, Z=2"

    def test_summary_single_hold(self):
        """Single hold should appear correctly."""
        items = [{"hold": "A"}]
        result = summary(items)
        assert result == "A=1"

    def test_summary_empty_items(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_summary_no_empty_holds_in_output(self):
        """Holds with empty values should not appear in summary."""
        items = [
            {"hold": "B"},
            {"hold": ""},
            {"hold": "A"},
        ]
        result = summary(items)
        assert result == "A=1, B=1"
        assert "" not in result

    def test_summary_case_sensitive_sorting(self):
        """Sorting should be case-sensitive (uppercase before lowercase in ASCII)."""
        items = [
            {"hold": "b"},
            {"hold": "A"},
            {"hold": "a"},
            {"hold": "B"},
        ]
        result = summary(items)
        # In Python, uppercase letters come before lowercase in default sorting
        assert result == "A=1, B=1, a=1, b=1"

    def test_summary_preserves_correct_counts_after_sorting(self):
        """Sorting should not affect the counts."""
        items = [
            {"hold": "C"},
            {"hold": "C"},
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=2, C=3"
