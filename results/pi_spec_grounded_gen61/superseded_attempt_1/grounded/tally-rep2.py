from tally.session import Session

def test_close_returns_running_total():
    """REQUIREMENT: `close()` returns the running total"""
    s = Session()
    s.add(5)
    assert s.close() == 5

def test_total_after_close_reports_zero():
    """REQUIREMENT: Calling `total()` after `close()` must report 0 until something new is added."""
    s = Session()
    s.add(7)
    s.close()
    assert s.total() == 0

def test_close_after_multiple_adds():
    """REQUIREMENT: `close()` returns the running total"""
    s = Session()
    s.add(1)
    s.add(2)
    s.add(3)
    assert s.close() == 6

def test_total_after_close_then_add():
    """REQUIREMENT: Calling `total()` after `close()` must report 0 until something new is added."""
    s = Session()
    s.add(100)
    s.close()
    assert s.total() == 0
    s.add(50)
    assert s.total() == 50