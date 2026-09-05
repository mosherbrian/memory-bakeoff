from tally.session import Session

s = Session()
s.add(3)
s.add(4)
assert s.total() == 7, f"A: total -> {s.total()}, expected 7"
assert s.close() == 7, f"B: close -> returned wrong total"
assert s.total() == 0, f"B: total after close -> {s.total()}, expected 0"
s.add(2)
assert s.total() == 2, f"B: reuse after close -> {s.total()}, expected 2"
print("VERIFIER OK")
