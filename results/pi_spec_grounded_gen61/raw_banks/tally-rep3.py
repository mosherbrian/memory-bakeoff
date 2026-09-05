from tally.session import Session


def test_close_returns_running_total():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    s.add(10)
    result = s.close()
    assert result == 10


def test_close_resets_session_to_zero():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.add(5)
    s.close()
    assert s.total() == 0


def test_total_after_close_reports_zero():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(7)
    s.close()
    assert s.total() == 0


def test_session_reusable_after_close():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.add(2)
    s.close()
    s.add(3)
    assert s.total() == 3


def test_close_on_empty_session_returns_zero():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    result = s.close()
    assert result == 0


def test_multiple_adds_before_close():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(1)
    s.add(2)
    s.add(3)
    result = s.close()
    assert result == 6


def test_close_resets_for_second_use():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(100)
    s.close()
    assert s.total() == 0
    s.add(50)
    assert s.total() == 50
