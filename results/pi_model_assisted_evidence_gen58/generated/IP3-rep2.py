import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Test that items with missing or empty hold are ignored in totals."""

    def test_ignores_missing_hold_key(self):
        """Items without a 'hold' key should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "B"},
            {"item": "widget"},  # no 'hold' key
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_ignores_empty_hold(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_ignores_none_hold(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_ignores_whitespace_only_hold(self):
        """Items with whitespace-only hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "   "},
            {"hold": "\t\n"},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_all_items_ignored(self):
        """If all items have missing/empty holds, result should be empty dict."""
        items = [
            {"item": "widget"},
            {"hold": ""},
            {"hold": None},
        ]
        result = totals(items)
        assert result == {}

    def test_normal_items_still_counted(self):
        """Normal items should still be counted correctly."""
        items = [
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 3, "B": 1}


class TestSummaryAlphabeticalOrder:
    """Test that summary lists holds in alphabetical order."""

    def test_summary_alphabetical_order(self):
        """Holds should be listed in alphabetical order in the summary."""
        items = [
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
            {"hold": "A"},
            {"hold": "B"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=2, B=3, C=1"

    def test_summary_single_hold(self):
        """Single hold should appear correctly."""
        items = [{"hold": "Z"}]
        result = summary(items)
        assert result == "Z=1"

    def test_summary_multiple_same_hold(self):
        """Multiple items in same hold should be counted and listed."""
        items = [
            {"hold": "M"},
            {"hold": "M"},
            {"hold": "M"},
        ]
        result = summary(items)
        assert result == "M=3"

    def test_summary_empty_list(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_summary_with_missing_holds_ignored(self):
        """Missing/empty holds should be ignored and remaining holds sorted."""
        items = [
            {"hold": "C"},
            {"hold": ""},
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=1, C=1"

    def test_summary_case_sensitive_order(self):
        """Holds should be sorted in standard alphabetical (case-sensitive) order."""
        items = [
            {"hold": "Z"},
            {"hold": "a"},
            {"hold": "A"},
            {"hold": "b"},
        ]
        result = summary(items)
        # In Python, uppercase letters come before lowercase in default sorting
        assert result == "A=1, Z=1, a=1, b=1"

    def test_summary_preserves_counts_with_sorting(self):
        """Sorting should not affect the counts."""
        items = [
            {"hold": "B"},
            {"hold": "A"},
            {"hold": "A"},
            {"hold": "C"},
            {"hold": "C"},
            {"hold": "C"},
        ]
        result = summary(items)
        assert result == "A=2, B=1, C=3"
