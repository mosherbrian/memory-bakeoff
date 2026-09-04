import sys
sys.path.insert(0, ".")
from tidewatch.fleet import Fleet
from tidewatch.summary import summarise

fleet = Fleet()
fleet.add("north quay", 1.0)
assert fleet.level("north quay", 2.5) == 1.5, "old behaviour changed"
assert summarise(fleet, {"north quay": 2.5}) == {"north quay": 1.5}, "old summarise changed"
assert fleet.level("north quay", 2.5, datum=0.5) == 2.0, "override not honoured by Fleet"
assert summarise(fleet, {"north quay": 2.5}, datum=0.5) == {"north quay": 2.0}, "override not honoured by summarise"
print("VERIFIER OK")
