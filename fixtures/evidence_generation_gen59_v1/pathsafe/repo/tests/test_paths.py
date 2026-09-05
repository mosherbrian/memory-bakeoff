from pathsafe.paths import resolve


def test_relative_name_lands_in_the_depot():
    assert resolve("parts.csv") == "depot/parts.csv"
