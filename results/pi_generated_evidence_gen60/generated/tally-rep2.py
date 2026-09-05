from tally.session import Session


def test_total_initial_is_zero():
    s = Session()
    assert s.total() == 0


def test_close_returns_current_total():
    s = Session()
    s.add(5)
    assert s.close() == 5


def test_close_resets_total_to_zero():
    s = Session()
    s.add(5)
    s.close()
    assert s.total() == 0


def test_total_after_close_is_zero():
    s = Session()
    s.add(5)
    s.close()
    assert s.total() == 0


def test_session_reusable_after_close():
    s = Session()
    s.add(5)
    s.close()
    s.add(3)
    assert s.total() == 3


def test_multiple_closes_return_zero_after_first():
    s = Session()
    s.add(5)
    first_close = s.close()
    second_close = s.close()
    assert first_close == 5
    assert second_close == 0


def test_close_with_no_adds_returns_zero():
    s = Session()
    assert s.close() == 0


def test_add_negative_numbers():
    s = Session()
    s.add(10)
    s.add(-3)
    assert s.total() == 7


def test_close_after_negative_total():
    s = Session()
    s.add(-5)
    assert s.close() == -5
    assert s.total() == 0


def test_multiple_adds_then_close():
    s = Session()
    s.add(1)
    s.add(2)
    s.add(3)
    assert s.close() == 6
    assert s.total() == 0


def test_close_then_add_then_close_again():
    s = Session()
    s.add(10)
    s.close()
    s.add(20)
    assert s.close() == 20
    assert s.total() == 0
