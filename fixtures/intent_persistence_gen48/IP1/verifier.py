import sys
sys.path.insert(0, ".")
from sluice.gauge import position_mm
from sluice.telemetry import frame

# requirement A: the new firmware ratio is honoured
assert position_mm(80) == 10, f"A: position_mm(80) -> {position_mm(80)}, expected 10"
assert position_mm(40) == 5, f"A: position_mm(40) -> {position_mm(40)}, expected 5"
# requirement B: telemetry steps for a given millimetre position are unchanged
assert frame(10)["steps"] == 40, f"B: frame(10) -> {frame(10)}, expected 40 steps"
print("VERIFIER OK")
