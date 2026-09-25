"""Hidden behaviour tests for bug U (not in the fixture). Run from a repo root."""
import sys; sys.path.insert(0, ".")
from src.seq import stable_unique
cases = [
    ('stable_unique([3, 1, 3, 2, 1])', [3, 1, 2], lambda: stable_unique([3, 1, 3, 2, 1])),
    ('stable_unique([])', [], lambda: stable_unique([])),
    ("stable_unique(['b', 'a', 'b'])", ['b', 'a'], lambda: stable_unique(['b', 'a', 'b'])),
    ('stable_unique([1, 2, 3])', [1, 2, 3], lambda: stable_unique([1, 2, 3])),
    ('stable_unique([5, 5, 5])', [5], lambda: stable_unique([5, 5, 5])),
]
bad = [(c, want, f()) for c, want, f in cases if f() != want]
print("hidden", "PASS" if not bad else "FAIL %r" % (bad,))
sys.exit(1 if bad else 0)
