from tally.session import Session


def test_close_returns_current_total():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    s.add(5)
    result = s.close()
    assert result == 5


def test_close_resets_session_to_zero():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.add(10)
    s.close()
    assert s.total() == 0


def test_total_after_close_reports_zero():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(7)
    s.close()
    assert s.total() == 0


def test_add_after_close_accumulates_from_zero():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(3)
    s.close()
    s.add(4)
    assert s.total() == 7


def test_close_returns_zero_if_nothing_added():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    result = s.close()
    assert result == 0


def test_multiple_close_calls():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(1)
    s.close()
    s.close()
    assert s.total() == 0


def test_add_negative_numbers():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(10)
    s.add(-3)
    assert s.total() == 7


def test_add_zero():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(0)
    assert s.total() == 0
