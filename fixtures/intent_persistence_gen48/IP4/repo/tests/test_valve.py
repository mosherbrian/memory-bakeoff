from lockgate.valve import clamp


def test_upper_bound():
    assert clamp(140) == 100
