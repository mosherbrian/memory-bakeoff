#!/bin/sh
# R43: durable participant transcript per arm (Tern 23:52Z). For each arm, once its worker snapshot exists,
# export the arm's fresh opencode session (id from the raw /new reply) to evidence/<arm>/participant-session.json.
R=/home/bmosher/memory-bake-off/campaign4/packages/R43-service-restoration-trial
for a in A-N A-I A-R C-R C-N C-I B-I B-R B-N; do
  until [ -f $R/evidence/$a/snapshot-at.txt ]; do sleep 10; done
  s=$(python -c "import json;print(json.load(open('$R/operator/new-$a.json'))['reply']['status'].split()[1])")
  timeout 120 opencode export $s > $R/evidence/$a/participant-session.json 2>$R/evidence/$a/participant-session.err
  echo "$(date -u +%FT%TZ) $a $s rc=$? bytes=$(wc -c < $R/evidence/$a/participant-session.json)" >> $R/operator/archive.log
done
