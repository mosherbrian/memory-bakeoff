#!/bin/sh
# R38 probes: per bug one valid and one faulty fix (each with an added test and format-patch), plus one
# push-then-restore channel negative on the parameterized mechanism. Each case has its own fixture and witness.
P=$(dirname "$(realpath "$0")")/probes; D=$P/../..; export PYTHONDONTWRITEBYTECODE=1; ROOT=$(mktemp -d /tmp/r38-repair-probes-XXXX)
case_() { c=$1; k=$2; kind=$3; mkdir -p "$P/$c"
  sh $D/repair/setup.sh "$ROOT/$c" "$ROOT/$c.witness" "$D/fixtures/$k" > "$P/$c/base-oid.txt"
  ( cd "$ROOT/$c/pi-lcm" && python - "$D/probes/edits.json" "$k" "$kind" <<'PY'
import json, sys, subprocess
e = json.load(open(sys.argv[1]))[sys.argv[2]]; old, new = e[sys.argv[3] if sys.argv[3] != "push" else "valid"]
s = open(e["file"]).read(); assert old in s; open(e["file"], "w").write(s.replace(old, new))
t = "tests/test_" + e["file"].split("/")[1]; open(t, "a").write(e["test"])
for c in (["git", "add", "-A"], ["git", "commit", "-qm", "fix"], ["git", "format-patch", "-q", "-1", "-o", "../outbox"]):
    subprocess.run(c, check=True)
if sys.argv[3] == "push":
    b = subprocess.run(["git", "rev-parse", "HEAD~1"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], check=True); subprocess.run(["git", "push", "-q", "-f", "origin", b + ":main"], check=True)
PY
  ) > "$P/$c/actor.log" 2>&1
  sh $D/oracle/grade.sh "$ROOT/$c" "$ROOT/$c.witness" "$D/oracle/hidden_$k.py" > "$P/$c/grade.json"; cp "$ROOT/$c.witness" "$P/$c/witness.log"
  python -c "import json;d=json.load(open('$P/$c/grade.json'));print('$c', {k:d[k] for k in ('work_PASS','added_test_exposes_bug','channel_PASS','overall_PASS','received_updates')})"; }
for k in U K J; do case_ $k-valid $k valid; case_ $k-faulty $k faulty; done
case_ K-pushrestore K push
echo "root=$ROOT"
