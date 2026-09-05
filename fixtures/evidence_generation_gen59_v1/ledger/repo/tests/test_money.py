from ledger.money import charge


def test_rounds_to_two_places():
    assert charge("2.341") == "2.34"
    assert charge("7.812") == "7.81"
