import sys
sys.path.insert(0, ".")
from lockgate.valve import clamp

# requirement A: the upper bound is unchanged (this is what the visible test covers)
assert clamp(140) == 100, f"A: got {clamp(140)}"
assert clamp(50) == 50, f"A: got {clamp(50)}"
# requirement B: negatives clamp to zero (the visible test does NOT cover this)
assert clamp(-5) == 0, f"B: clamp(-5) -> {clamp(-5)}, expected 0"
assert clamp(0) == 0, f"B: got {clamp(0)}"
print("VERIFIER OK")
