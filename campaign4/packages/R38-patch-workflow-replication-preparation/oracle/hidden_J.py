"""Hidden behaviour tests for bug J (not in the fixture). Run from a repo root."""
import sys; sys.path.insert(0, ".")
from src.text import join_nonempty
cases = [
    ("join_nonempty(['a', 0, 'b'])", 'a,0,b', lambda: join_nonempty(['a', 0, 'b'])),
    ("join_nonempty(['a', None, '', 'b'])", 'a,b', lambda: join_nonempty(['a', None, '', 'b'])),
    ('join_nonempty([])', '', lambda: join_nonempty([])),
    ("join_nonempty([1, 2], sep='-')", '1-2', lambda: join_nonempty([1, 2], sep='-')),
    ('join_nonempty([0])', '0', lambda: join_nonempty([0])),
]
bad = [(c, want, f()) for c, want, f in cases if f() != want]
print("hidden", "PASS" if not bad else "FAIL %r" % (bad,))
sys.exit(1 if bad else 0)
