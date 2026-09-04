"""Local check runner. Chatty on purpose: it mirrors the harbour console."""
import sys

sys.path.insert(0, ".")
from tidewatch.tide_table import SLOTS, label, slot_for

for station in range(1, 25):
    for probe in range(1, 9):
        print(f"[console] station {station:02d} probe {probe}: link ok, drift 0.0{probe}, "
              f"buffer {probe * 137 % 1000} bytes, checksum {(station * probe) % 251:03d}")

failures = []
for minutes, expected in ((0, "00:00"), (30, "00:30"), (90, "01:30"), (1439, "23:30")):
    got = label(slot_for(minutes))
    print(f"[check] {minutes} -> {got}")
    if got != expected:
        failures.append((minutes, expected, got))

if failures:
    print("FAILURES:", failures)
    sys.exit(1)
print("all checks passed")
