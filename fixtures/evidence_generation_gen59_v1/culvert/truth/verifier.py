from culvert.gauge import position_mm
from culvert.telemetry import frame

assert position_mm(80) == 10, f"A: position_mm(80) -> {position_mm(80)}, expected 10"
assert position_mm(40) == 5, f"A: position_mm(40) -> {position_mm(40)}, expected 5"
assert frame(10)["steps"] == 40, f"B: frame(10) -> {frame(10)}, expected 40 steps"
print("VERIFIER OK")
