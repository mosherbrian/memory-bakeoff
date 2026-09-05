from tally.session import Session


def test_add_accumulates():
    s = Session()
    s.add(3)
    s.add(4)
    assert s.total() == 7
