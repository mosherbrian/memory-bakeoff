from tally.session import Session

def test_close_returns_running_total():
    """REQUIREMENT: close() returns the running total AND resets the session to zero"""
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
    s.add(3)
    s.close()
    assert s.total() == 0

def test_add_after_close_starts_from_zero():
    """REQUIREMENT: Calling total() after close() must report 0 until something new is added."""
    s = Session()
    s.add(2)
    s.close()
    s.add(7)
    assert s.total() == 7

def test_close_on_empty_session_returns_zero():
    """REQUIREMENT: close() returns the running total AND resets the session to zero"""
    s = Session()
    result = s.close()
    assert result == 0

def test_close_on_empty_session_resets_to_zero():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.close()
    assert s.total() == 0

def test_multiple_close_calls():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.add(1)
    s.close()
    s.add(2)
    s.close()
    s.add(3)
    assert s.total() == 3

def test_negative_values():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(-5)
    assert s.total() == -5

def test_add_zero():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(0)
    assert s.total() == 0