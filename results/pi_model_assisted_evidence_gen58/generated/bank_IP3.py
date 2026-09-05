# --- IP3-rep1 ---
import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Tests for totals() ignoring items with missing or empty hold."""

    def test_r1_ignores_missing_hold_key(self):
        """Items without a 'hold' key should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "B"},
            {"item": "widget"},  # no hold key
        ]
        result = totals(items)
        assert "widget" not in result
        assert result == {"A": 1, "B": 1}

    def test_r1_ignores_empty_hold(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert "" not in result
        assert result == {"A": 1, "B": 1}

    def test_r1_ignores_none_hold(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert None not in result
        assert result == {"A": 1, "B": 1}

    def test_r1_ignores_whitespace_hold(self):
        """Items with whitespace-only hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "   "},
            {"hold": "B"},
        ]
        result = totals(items)
        assert "   " not in result
        assert result == {"A": 1, "B": 1}

    def test_r1_all_items_have_missing_hold(self):
        """When all items are missing hold, result should be empty dict."""
        items = [
            {"item": "widget1"},
            {"item": "widget2"},
        ]
        result = totals(items)
        assert result == {}

    def test_r1_all_items_have_empty_hold(self):
        """When all items have empty hold, result should be empty dict."""
        items = [
            {"hold": ""},
            {"hold": ""},
        ]
        result = totals(items)
        assert result == {}

    def test_r1_mixed_valid_and_invalid_holds(self):
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

    def test_r1_summary_orders_holds_alphabetically(self):
        """Holds should be listed in alphabetical order."""
        items = [
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=1, C=1"

    def test_r1_summary_orders_multiple_items_same_hold(self):
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

    def test_r1_summary_single_hold(self):
        """Single hold should appear as-is."""
        items = [{"hold": "A"}]
        result = summary(items)
        assert result == "A=1"

    def test_r1_summary_empty_items(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_r1_summary_orders_case_sensitive(self):
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

    def test_r1_summary_ignores_invalid_holds_in_ordering(self):
        """Items with missing/empty/None holds should not appear in summary."""
        items = [
            {"hold": "B"},
            {"hold": ""},
            {"hold": "A"},
            {"hold": None},
        ]
        result = summary(items)
        assert result == "A=1, B=1"

    def test_r1_summary_complex_ordering(self):
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


# --- IP3-rep2 ---
import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Test that items with missing or empty hold are ignored in totals."""

    def test_r2_ignores_missing_hold_key(self):
        """Items without a 'hold' key should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "B"},
            {"item": "widget"},  # no 'hold' key
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_r2_ignores_empty_hold(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_r2_ignores_none_hold(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_r2_ignores_whitespace_only_hold(self):
        """Items with whitespace-only hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": "   "},
            {"hold": "\t\n"},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}

    def test_r2_all_items_ignored(self):
        """If all items have missing/empty holds, result should be empty dict."""
        items = [
            {"item": "widget"},
            {"hold": ""},
            {"hold": None},
        ]
        result = totals(items)
        assert result == {}

    def test_r2_normal_items_still_counted(self):
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

    def test_r2_summary_alphabetical_order(self):
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

    def test_r2_summary_single_hold(self):
        """Single hold should appear correctly."""
        items = [{"hold": "Z"}]
        result = summary(items)
        assert result == "Z=1"

    def test_r2_summary_multiple_same_hold(self):
        """Multiple items in same hold should be counted and listed."""
        items = [
            {"hold": "M"},
            {"hold": "M"},
            {"hold": "M"},
        ]
        result = summary(items)
        assert result == "M=3"

    def test_r2_summary_empty_list(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_r2_summary_with_missing_holds_ignored(self):
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

    def test_r2_summary_case_sensitive_order(self):
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

    def test_r2_summary_preserves_counts_with_sorting(self):
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


# --- IP3-rep3 ---
import pytest
from tally.counter import totals
from tally.report import summary


class TestTotalsMissingHold:
    """Tests for ignoring items with missing or empty hold keys."""

    def test_r3_ignores_missing_hold_key(self):
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

    def test_r3_ignores_empty_hold_value(self):
        """Items with an empty string hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": ""},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}
        assert "" not in result

    def test_r3_ignores_none_hold_value(self):
        """Items with None hold should be ignored."""
        items = [
            {"hold": "A"},
            {"hold": None},
            {"hold": "B"},
        ]
        result = totals(items)
        assert result == {"A": 1, "B": 1}
        assert None not in result

    def test_r3_ignores_all_items_with_empty_holds(self):
        """When all items have empty holds, result should be empty dict."""
        items = [
            {"hold": ""},
            {"hold": ""},
        ]
        result = totals(items)
        assert result == {}

    def test_r3_ignores_all_items_with_missing_holds(self):
        """When all items are missing hold key, result should be empty dict."""
        items = [
            {"cargo": "x"},
            {"cargo": "y"},
        ]
        result = totals(items)
        assert result == {}

    def test_r3_valid_hold_not_affected(self):
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

    def test_r3_summary_sorted_alphabetically(self):
        """Holds should be listed in alphabetical order."""
        items = [
            {"hold": "C"},
            {"hold": "A"},
            {"hold": "B"},
        ]
        result = summary(items)
        assert result == "A=1, B=1, C=1"

    def test_r3_summary_sorted_with_multiple_items_per_hold(self):
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

    def test_r3_summary_single_hold(self):
        """Single hold should appear correctly."""
        items = [{"hold": "A"}]
        result = summary(items)
        assert result == "A=1"

    def test_r3_summary_empty_items(self):
        """Empty items list should produce empty string."""
        result = summary([])
        assert result == ""

    def test_r3_summary_no_empty_holds_in_output(self):
        """Holds with empty values should not appear in summary."""
        items = [
            {"hold": "B"},
            {"hold": ""},
            {"hold": "A"},
        ]
        result = summary(items)
        assert result == "A=1, B=1"
        assert "" not in result

    def test_r3_summary_case_sensitive_sorting(self):
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

    def test_r3_summary_preserves_correct_counts_after_sorting(self):
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
