#!/usr/bin/env python3
"""R14 arm manifests. Deterministic: relative path -> sha256 for every file,
excluding ONLY Python caches (any __pycache__/ directory, *.pyc, .pytest_cache/),
which running the allowed check creates.

  manifest.py build DIR > manifest.json
  manifest.py compare MANIFEST DIR --frozen igw,tests     # phase 1: both frozen
  manifest.py compare MANIFEST DIR --frozen tests         # phase 2: tests frozen
Compare prints every added, missing and changed file and says which are in a
frozen area. Exit 0 only if no frozen-area difference and no file outside
igw/ and tests/ changed; 1 otherwise. notes/ is ignored (ordinary work notes)."""
import hashlib, json, os, sys

def cached(rel):
    parts = rel.split("/")
    return "__pycache__" in parts or ".pytest_cache" in parts or rel.endswith(".pyc")

def build(root):
    out = {}
    for d, dirs, files in os.walk(root):
        dirs.sort()
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), root)
            if not cached(rel):
                out[rel] = hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest()
    return dict(sorted(out.items()))

def compare(man, root, frozen):
    old, new = json.load(open(man)), build(root)
    diffs = [("added", r) for r in new if r not in old] + [("missing", r) for r in old if r not in new] \
        + [("changed", r) for r in old if r in new and old[r] != new[r]]
    bad = 0
    for kind, r in sorted(diffs, key=lambda x: x[1]):
        top = r.split("/")[0]
        if top == "notes":
            continue
        frz = top in frozen or top not in ("igw", "tests")
        bad += frz
        print(f"{'FROZEN ' if frz else 'allowed'} {kind:7} {r}")
    print(f"{len(old)} frozen-manifest files, {len(new)} now (caches excluded); {bad} frozen-area differences")
    return 1 if bad else 0

if __name__ == "__main__":
    if sys.argv[1] == "build":
        json.dump(build(sys.argv[2]), sys.stdout, indent=1)
    else:
        sys.exit(compare(sys.argv[2], sys.argv[3], sys.argv[5].split(",") if len(sys.argv) > 5 else ["igw", "tests"]))
