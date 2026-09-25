from src.seq import stable_unique


def test_already_unique_sorted():
    assert stable_unique([1, 2, 3]) == [1, 2, 3]
