from src.window import last_n


def test_last_two():
    assert last_n([1, 2, 3], 2) == [2, 3]
