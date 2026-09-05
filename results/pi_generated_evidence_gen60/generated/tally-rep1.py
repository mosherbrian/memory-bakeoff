import pytest
from tally.session import Session


class TestSessionTotal:
    """Tests for total() reporting the running total."""

    def test_total_starts_at_zero(self):
        s = Session()
        assert s.total() == 0

    def test_total_after_add(self):
        s = Session()
        s.add(5)
        assert s.total() == 5

    def test_total_after_multiple_adds(self):
        s = Session()
        s.add(10)
        s.add(20)
        s.add(30)
        assert s.total() == 60

    def test_total_with_negative_numbers(self):
        s = Session()
        s.add(10)
        s.add(-3)
        assert s.total() == 7


class TestSessionClose:
    """Tests for close() returning the running total and resetting to zero."""

    def test_close_returns_total(self):
        s = Session()
        s.add(7)
        assert s.close() == 7

    def test_close_resets_total_to_zero(self):
        s = Session()
        s.add(15)
        s.close()
        assert s.total() == 0

    def test_close_on_empty_session_returns_zero(self):
        s = Session()
        assert s.close() == 0
        assert s.total() == 0

    def test_close_multiple_times(self):
        s = Session()
        s.add(10)
        assert s.close() == 10
        s.add(5)
        assert s.close() == 5
        assert s.total() == 0

    def test_total_after_close_reports_zero(self):
        s = Session()
        s.add(100)
        s.close()
        assert s.total() == 0

    def test_session_reusable_after_close(self):
        s = Session()
        s.add(10)
        s.close()
        s.add(20)
        assert s.total() == 20

    def test_session_reusable_after_close_accumulates_from_zero(self):
        s = Session()
        s.add(5)
        s.close()
        s.add(3)
        s.add(7)
        assert s.total() == 10

    def test_close_does_not_affect_total_before_close(self):
        s = Session()
        s.add(42)
        assert s.total() == 42
        result = s.close()
        assert result == 42
        assert s.total() == 0


class TestSessionEdgeCases:
    """Edge case tests for Session behavior."""

    def test_add_zero(self):
        s = Session()
        s.add(0)
        assert s.total() == 0

    def test_add_negative_numbers(self):
        s = Session()
        s.add(-5)
        s.add(-3)
        assert s.total() == -8

    def test_add_then_close_then_add(self):
        s = Session()
        s.add(10)
        s.close()
        s.add(-5)
        assert s.total() == -5

    def test_close_returns_current_total_not_a_copy(self):
        s = Session()
        s.add(10)
        returned = s.close()
        assert returned == 10
        assert s.total() == 0

    def test_multiple_close_calls_return_correct_values(self):
        s = Session()
        s.add(1)
        assert s.close() == 1
        s.add(2)
        assert s.close() == 2
        s.add(3)
        assert s.close() == 3
        assert s.total() == 0
