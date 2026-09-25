"""Hidden behaviour tests (not in the fixture). Run from a repo root: python hidden_test.py"""
import sys; sys.path.insert(0, ".")
from src.window import last_n
cases = [(([1, 2, 3], 0), []), (([1, 2, 3], 2), [2, 3]), (([], 3), []), (([1, 2], 5), [1, 2])]
bad = [(a, want, last_n(list(a[0]), a[1])) for a, want in cases if last_n(list(a[0]), a[1]) != want]
print("hidden", "PASS" if not bad else f"FAIL {bad}")
sys.exit(1 if bad else 0)
