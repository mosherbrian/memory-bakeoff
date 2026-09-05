from tally.session import Session

def test_close_returns_running_total():
    """REQUIREMENT: close() returns the running total AND resets the session to zero"""
    s = Session()
    s.add(5)
    result = s.close()
    assert result == 5

def test_add_zero():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(0)
    assert s.total() == 0
from tally.session import Session

def test_close_returns_current_total():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    s.add(5)
    result = s.close()
    assert result == 5

def test_add_zero():
    """REQUIREMENT: add(n) adds n to the running total."""
    s = Session()
    s.add(0)
    assert s.total() == 0
from tally.session import Session

def test_close_returns_running_total():
    """REQUIREMENT: close() returns the running total"""
    s = Session()
    s.add(10)
    result = s.close()
    assert result == 10

def test_session_reusable_after_close():
    """REQUIREMENT: close() returns the running total AND resets the session to zero, so that a session reused after close() starts from zero again."""
    s = Session()
    s.add(2)
    s.close()
    s.add(3)
    assert s.total() == 3