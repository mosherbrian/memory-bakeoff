import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Tests for totals() ignoring items with missing or empty hold."""

    def test_ignores_missing_hold_key(self):
        """Items without a 'hold' key should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "B"},
            {"item": "widget"},  # no hold key
        ]
        result = totals(items)
        assert "widget" not in result
        assert result == {"A": 1, "B": 1}

    def test_ignores_empty_hold(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert "" not in result
        assert result == {"A": 1, "B": 1}

    def test_ignores_none_hold(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert None not in result
        assert result == {"A": 1, "B": 1}

    def test_ignores_whitespace_hold(self):
        """Items with whitespace-only hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "   "},
            {"hold": "B"},
        ]
        result = totals(items)
        assert "   " not in result
        assert result == {"A": 1, "B": 1}

    def test_all_items_have_missing_hold(self):
        """When all items are missing hold, result should be empty dict."""
        items = [
            {"item": "widget1"},
            {"item": "widget2"},
        ]
        result = totals(items)
        assert result == {}

    def test_all_items_have_empty_hold(self):
        """When all items have empty hold, result should be empty dict."""
        items = [
            {"hold": ""},
            {"hold": ""},
        ]
        result = totals(items)
        assert result == {}

    def test_mixed_valid_and_invalid_holds(self):
        """Valid holds are counted, invalid ones are skipped."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
            {"hold": None},
            {"hold": "A"},
        ]
        result = totals(items)
        assert result == {"A": 2, "B": 1}


class TestSummaryAlphabeticalOrder:
    """Tests for summary() listing holds in alphabetical order."""

    def test_summary_orders_holds_alphabetically(self):
        """Holds should be listed in alphabetical order."""
        items = [
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=1, C=1"

    def test_summary_orders_multiple_items_same_hold(self):
        """Holds with multiple items should still be ordered alphabetically."""
        items = [
            {"hold": "Z"},
            {"hold": "A"},
            {"hold": "Z"},
            {"hold": "M"},
            {"hold": "A"},
        ]
        result = summary(items)
        assert result == "A=2, M=1, Z=2"

    def test_summary_single_hold(self):
        """Single hold should appear as-is."""
        items = [{"hold": "A"}]
        result = summary(items)
        assert result == "A=1"

    def test_summary_empty_items(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_summary_orders_case_sensitive(self):
        """Alphabetical ordering should be case-sensitive (standard string sort)."""
        items = [
            {"hold": "b"},
            {"hold": "A"},
            {"hold": "a"},
            {"hold": "B"},
        ]
        result = summary(items)
        # Standard Python string sorting: uppercase before lowercase
        assert result == "A=1, B=1, a=1, b=1"

    def test_summary_ignores_invalid_holds_in_ordering(self):
        """Items with missing/empty/None holds should not appear in summary."""
        items = [
            {"hold": "B"},
            {"hold": ""},
            {"hold": "A"},
            {"hold": None},
        ]
        result = summary(items)
        assert result == "A=1, B=1"

    def test_summary_complex_ordering(self):
        """Test with more holds to ensure consistent alphabetical ordering."""
        items = [
            {"hold": "Delta"},
            {"hold": "Alpha"},
            {"hold": "Charlie"},
            {"hold": "Bravo"},
            {"hold": "Alpha"},
            {"hold": "Charlie"},
        ]
        result = summary(items)
        assert result == "Alpha=2, Bravo=1, Charlie=2, Delta=1"
