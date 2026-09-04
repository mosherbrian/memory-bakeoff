import sys
sys.path.insert(0, ".")
from tidewatch.rounding import normalise

for value, expected in ((1.005, 1.01), (-1.005, -1.01), (2.675, 2.68), (-2.675, -2.68),
                        (0.0, 0.0), (1.004, 1.0), (-1.004, -1.0)):
    got = normalise(value)
    assert got == expected, f"normalise({value}) -> {got}, expected {expected}"
print("VERIFIER OK")
