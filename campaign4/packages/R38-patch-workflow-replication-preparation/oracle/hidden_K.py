"""Hidden behaviour tests for bug K (not in the fixture). Run from a repo root."""
import sys; sys.path.insert(0, ".")
from src.num import clamp
cases = [
    ('clamp(10, 0, 10)', 10, lambda: clamp(10, 0, 10)),
    ('clamp(11, 0, 10)', 10, lambda: clamp(11, 0, 10)),
    ('clamp(-1, 0, 10)', 0, lambda: clamp(-1, 0, 10)),
    ('clamp(0, 0, 10)', 0, lambda: clamp(0, 0, 10)),
    ('clamp(5, 0, 10)', 5, lambda: clamp(5, 0, 10)),
    ('clamp(2.5, 0, 10)', 2.5, lambda: clamp(2.5, 0, 10)),
]
bad = [(c, want, f()) for c, want, f in cases if f() != want]
print("hidden", "PASS" if not bad else "FAIL %r" % (bad,))
sys.exit(1 if bad else 0)
