import sys
sys.path.insert(0, ".")
from tidewatch.tide_table import label, slot_for

cases = ((0, "00:00"), (30, "00:30"), (90, "01:30"), (1439, "23:30"), (60, "01:00"), (750, "12:30"))
for minutes, expected in cases:
    got = label(slot_for(minutes))
    assert got == expected, f"{minutes} -> {got}, expected {expected}"
print("VERIFIER OK")
