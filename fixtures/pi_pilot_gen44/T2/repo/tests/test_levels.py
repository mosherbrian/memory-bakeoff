from tidewatch.fleet import Fleet
from tidewatch.summary import summarise


def test_levels_are_relative_to_datum():
    fleet = Fleet()
    fleet.add("north quay", 1.0)
    assert summarise(fleet, {"north quay": 2.5}) == {"north quay": 1.5}
