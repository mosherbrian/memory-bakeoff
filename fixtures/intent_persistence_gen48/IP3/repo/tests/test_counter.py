from tally.counter import totals


def test_counts_by_hold():
    assert totals([{"hold": "A"}, {"hold": "A"}, {"hold": "B"}]) == {"A": 2, "B": 1}
