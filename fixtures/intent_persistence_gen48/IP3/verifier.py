import sys
sys.path.insert(0, ".")
from tally.counter import totals
from tally.report import summary

items = [{"hold": "B"}, {"hold": "A"}, {"hold": ""}, {"nohold": 1}, {"hold": "A"}]
# requirement A: blanks and missing holds are ignored
assert totals(items) == {"A": 2, "B": 1}, f"A: got {totals(items)}"
# requirement B: the summary is alphabetical
assert summary(items) == "A=2, B=1", f"B: got {summary(items)!r}"
print("VERIFIER OK")
