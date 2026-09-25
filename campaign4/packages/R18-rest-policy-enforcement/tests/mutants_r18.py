#!/usr/bin/env python3
"""R18 planted-fault harness: mutates the CANDIDATE and runs the R18 suite.
Each mutant must be killed (suite fails). Run: python3 tests/mutants_r18.py"""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CAND = os.path.join(PKG, "candidate", "research-gap-check")
SUITE = os.path.join(HERE, "test_r18_rest_policy.py")
SRC = open(CAND).read()
M = {
  "overlong-accepted": ("if v - e > REST_MAX_S:", "if False and v - e > REST_MAX_S:"),
  "prose-accepted": ('    if not isinstance(step, dict):\n        return "prose-only rest: structured next_step required"', '    if not isinstance(step, dict):\n        return None'),
  "invalid-extends": ("        return None, bad\n    if NOW < v:", "        return r, bad\n    if NOW < v:"),
  "whitespace-objective-accepted": ('    if not str(rec.get("objective") or "").strip():\n        return "receipt missing objective"\n    if str(rec.get("objective")).strip().lower() in SENTINELS:', '    if False and str(rec.get("objective") or "").strip():\n        return "receipt missing objective"\n    if False and str(rec.get("objective")).strip().lower() in SENTINELS:'),
  "receipt-unchecked": ("    prob = validate_step(q, r.get(\"next_step\"), v)", "    prob = None"),
}
bad = 0
for name, (a, b) in M.items():
    assert SRC.count(a) == 1, f"mutant {name}: anchor not unique/found"
    f = tempfile.NamedTemporaryFile("w", suffix="-mut", delete=False)
    f.write(SRC.replace(a, b, 1)); f.close()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", SUITE],
                       env=dict(os.environ, R18_CHECK=f.name), capture_output=True, text=True, cwd=PKG)
    os.unlink(f.name)
    caught = r.returncode != 0
    bad += not caught
    print(f"{'CAUGHT ' if caught else 'SURVIVED'} {name}")
print(f"{len(M)-bad}/{len(M)} caught")
sys.exit(1 if bad else 0)
