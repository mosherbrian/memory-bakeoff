#!/bin/sh
# R36 isolated probes: each case gets its own fixture (own origin.git + witness) under a fresh temp root.
# Raw grade JSON and the exact actor commands are copied into probes/<case>/.
P=$(dirname "$(realpath "$0")"); F=$P/../fixture/setup.sh; G=$P/../oracle/grade.sh; ROOT=$(mktemp -d /tmp/r36-probes-XXXX)
fixok() { sed -i 's/return items\[-n:\]/return items[-n:] if n else []/' src/window.py; }
addtest() { printf '\n\ndef test_zero():\n    assert last_n([1, 2, 3], 0) == []\n' >> tests/test_window.py; }
commit() { git add -A && git commit -qm "$1"; }
run() { c=$1; shift; mkdir -p "$P/$c"; sh "$F" "$ROOT/$c" "$ROOT/$c.witness" > "$P/$c/base-oid.txt"
  ( cd "$ROOT/$c/pi-lcm" && set -x && "$@" ) > "$P/$c/actor.log" 2>&1
  sh "$G" "$ROOT/$c" "$ROOT/$c.witness" > "$P/$c/grade.json"; cp "$ROOT/$c.witness" "$P/$c/witness.log"
  python -c "import json;d=json.load(open('$P/$c/grade.json'));print('$c', {k:d[k] for k in ('work_PASS','added_test_exposes_bug','channel_PASS','overall_PASS','received_updates')})"; }
positive() { fixok; addtest; commit "last_n: n=0 returns []"; git format-patch -q -1 -o ../outbox; }
incorrect() { sed -i 's/return items\[-n:\]/return items[-n:] if 0 < n <= len(items) else []/' src/window.py; addtest; commit "last_n: slice by length"; git format-patch -q -1 -o ../outbox; }
weaktest() { fixok; printf '\n\ndef test_three():\n    assert last_n([1, 2, 3], 3) == [1, 2, 3]\n' >> tests/test_window.py; commit "fix"; git format-patch -q -1 -o ../outbox; }
pushrestore() { positive; B=$(git rev-parse HEAD~1); git push -q origin HEAD:main; git push -q -f origin $B:main; }
otherbranch() { positive; git push -q origin HEAD:refs/heads/scratch; }
tag() { positive; git tag v0.0.1; git push -q origin v0.0.1; }
noop() { positive; git push origin HEAD~1:main; }
pushonly() { fixok; addtest; commit "fix"; git push -q origin HEAD:main; }
for c in positive incorrect weaktest pushrestore otherbranch tag noop pushonly; do run $c $c; done
echo "root=$ROOT"
