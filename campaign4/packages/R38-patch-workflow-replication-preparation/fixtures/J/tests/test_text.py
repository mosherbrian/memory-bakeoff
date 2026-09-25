from src.text import join_nonempty


def test_two_words():
    assert join_nonempty(["a", "b"]) == "a,b"
