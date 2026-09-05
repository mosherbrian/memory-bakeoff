from tally.session import Session


def test_close_returns_running_total():
    """REQUIREMENT: `close()` returns the running total"""
    s = Session()
    s.add(5)
    s.add(10)
    result = s.close()
    assert result == 15


def test_close_resets_session_to_zero():
    """REQUIREMENT: `close()` ... resets the session to zero, so that a session reused after `close()` starts from zero again."""
    s = Session()
    s.add(20)
    s.close()
    assert s.total() == 0


def test_total_after_close_reports_zero():
    """REQUIREMENT: Calling `total()` after `close()` must report 0 until something new is added."""
    s = Session()
    s.add(100)
    s.close()
    assert s.total() == 0


def test_add_after_close_accumulates_from_zero():
    """REQUIREMENT: `add(n)` adds n to the running total."""
    s = Session()
    s.add(5)
    s.close()
    s.add(3)
    assert s.total() == 3


def test_multiple_close_calls_return_correct_totals():
    """REQUIREMENT: `close()` returns the running total AND resets the session to zero"""
    s = Session()
    s.add(1)
    assert s.close() == 1
    assert s.total() == 0
    s.add(2)
    s.add(3)
    assert s.close() == 5
    assert s.total() == 0


def test_close_on_empty_session_returns_zero():
    """REQUIREMENT: `close()` returns the running total"""
    s = Session()
    assert s.close() == 0
    assert s.total() == 0
