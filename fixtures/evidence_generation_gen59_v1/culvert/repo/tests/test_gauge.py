from culvert.gauge import position_mm


def test_position_is_millimetres():
    assert position_mm(40) == 10
