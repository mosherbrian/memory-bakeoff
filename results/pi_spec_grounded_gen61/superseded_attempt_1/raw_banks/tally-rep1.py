from tally.session import Session


def test_close_returns_total():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    s.add(5)
    result = s.close()
    assert result == 5


def test_close_resets_session_to_zero():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    s.add(10)
    s.close()
    assert s.total() == 0


def test_total_after_close_reports_zero():
    """REQUIREMENT: Calling `total()` after `close()` must report 0 until something new is added."""
    s = Session()
    s.add(7)
    s.close()
    assert s.total() == 0


def test_add_after_close_starts_from_zero():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    s.add(2)
    s.close()
    s.add(3)
    assert s.total() == 3


def test_close_on_empty_session():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    result = s.close()
    assert result == 0
    assert s.total() == 0


def test_multiple_adds_before_close():
    """REQUIREMENT: `add(n)` adds n to the running total. `total()` reports the running total."""
    s = Session()
    s.add(1)
    s.add(2)
    s.add(3)
    assert s.total() == 6
    result = s.close()
    assert result == 6
    assert s.total() == 0


def test_close_then_add_then_close():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    s.add(10)
    first_close = s.close()
    assert first_close == 10
    s.add(5)
    second_close = s.close()
    assert second_close == 5
    assert s.total() == 0
