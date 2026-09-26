#!/bin/sh
# sh session.sh 1|2 LABEL OPDIR PROMPTFILE   (no set -e: exit code always recorded)
set -u; N=$1; L=$2; OP=$3; PR=$4; . /home/bmosher/memory-bake-off/campaign4/packages/R47-restart-trial-preparation/stub/common.sh
W=$(python -c "import json;print(json.load(open('$OP/$L.arm.json'))['cwd'])")
SID=$(python -c "import uuid;print(uuid.uuid4())"); echo "session_id=$SID" > $OP/$L.s$N.meta; date -u +start=%FT%TZ >> $OP/$L.s$N.meta
TXT=$(sed "s#<CWD>#$W#g" "$PR")
cd "$W" || { echo "cd_failed" >> $OP/$L.s$N.meta; exit 0; }
if [ "$N" = 1 ]; then $ENVI claude -p --session-id $SID $BASE $S1_TOOLS "$TXT" > $OP/$L.s1.jsonl 2> $OP/$L.s1.stderr
else $ENVI claude -p --session-id $SID $BASE $S2_TOOLS --settings "$S2_SETTINGS" "$TXT" > $OP/$L.s2.jsonl 2> $OP/$L.s2.stderr; fi
rc=$?; echo "exit=$rc" >> $OP/$L.s$N.meta; date -u +end=%FT%TZ >> $OP/$L.s$N.meta; exit 0
