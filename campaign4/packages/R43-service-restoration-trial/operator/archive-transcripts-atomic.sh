#!/bin/sh
# R43 transcript archiver, atomic (Tern 00:03Z): export to a temp file in the same folder, check it parses as
# JSON, then rename into evidence/<arm>/participant-session.json. Remaining arms only; earlier ones already archived.
R=/home/bmosher/memory-bake-off/campaign4/packages/R43-service-restoration-trial
for a in B-I B-R B-N; do
  until [ -f $R/evidence/$a/snapshot-at.txt ]; do sleep 5; done
  s=$(python -c "import json;print(json.load(open('$R/operator/new-$a.json'))['reply']['status'].split()[1])")
  t=$R/evidence/$a/.participant-session.json.tmp
  timeout 120 opencode export $s > $t 2>$R/evidence/$a/participant-session.err; rc=$?
  if [ $rc = 0 ] && python -c "import json;json.load(open('$t'))" 2>/dev/null; then mv $t $R/evidence/$a/participant-session.json; ok=published; else ok="NOT published (rc=$rc or not JSON)"; fi
  echo "$(date -u +%FT%TZ) $a $s rc=$rc $ok bytes=$(wc -c < $R/evidence/$a/participant-session.json 2>/dev/null || echo 0)" >> $R/operator/archive.log
done
