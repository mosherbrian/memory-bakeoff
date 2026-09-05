import pytest
from tally.session import Session


class TestSessionTotal:
    """Tests for Session.total() behavior."""

    def test_initial_total_is_zero(self):
        s = Session()
        assert s.total() == 0

    def test_total_after_add(self):
        s = Session()
        s.add(5)
        assert s.total() == 5

    def test_total_after_multiple_adds(self):
        s = Session()
        s.add(2)
        s.add(3)
        s.add(10)
        assert s.total() == 15

    def test_total_with_negative_numbers(self):
        s = Session()
        s.add(10)
        s.add(-4)
        assert s.total() == 6

    def test_total_with_zero(self):
        s = Session()
        s.add(0)
        assert s.total() == 0


class TestSessionClose:
    """Tests for Session.close() behavior."""

    def test_close_returns_current_total(self):
        s = Session()
        s.add(7)
        s.add(3)
        result = s.close()
        assert result == 10

    def test_close_resets_total_to_zero(self):
        s = Session()
        s.add(100)
        s.close()
        assert s.total() == 0

    def test_close_on_empty_session_returns_zero(self):
        s = Session()
        result = s.close()
        assert result == 0
        assert s.total() == 0

    def test_close_multiple_times(self):
        s = Session()
        s.add(5)
        first_close = s.close()
        assert first_close == 5
        assert s.total() == 0

        s.add(3)
        second_close = s.close()
        assert second_close == 3
        assert s.total() == 0

    def test_total_after_close_is_zero(self):
        s = Session()
        s.add(10)
        s.close()
        assert s.total() == 0

    def test_session_reuse_after_close(self):
        s = Session()
        s.add(5)
        s.close()
        s.add(2)
        assert s.total() == 2

    def test_session_reuse_after_close_multiple_adds(self):
        s = Session()
        s.add(10)
        s.close()
        s.add(1)
        s.add(2)
        s.add(3)
        assert s.total() == 6

    def test_close_does_not_affect_other_sessions(self):
        s1 = Session()
        s2 = Session()
        s1.add(10)
        s2.add(20)
        s1.close()
        assert s1.total() == 0
        assert s2.total() == 20
