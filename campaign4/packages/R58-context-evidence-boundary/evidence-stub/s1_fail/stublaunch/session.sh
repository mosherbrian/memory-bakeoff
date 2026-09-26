#!/bin/sh
# R50 copy of R48 session.sh: also records the exact argv (prompt as its sha256) before launch.
# sh session.sh 1|2 LABEL OPDIR PROMPTFILE   (no set -e: exit code always recorded)
set -u; N=$1; L=$2; OP=$3; PR=$4; . "$(dirname "$0")/common.sh"
W=$(python -c "import json;print(json.load(open('$OP/$L.arm.json'))['cwd'])")
SID=$(python -c "import uuid;print(uuid.uuid4())"); echo "session_id=$SID" > $OP/$L.s$N.meta; date -u +start=%FT%TZ >> $OP/$L.s$N.meta
TXT=$(sed "s#<CWD>#$W#g" "$PR")
printf '%s\n' "$TXT" > "$OP/$L.s$N.prompt.txt"
sha256sum "$PR" "$(dirname "$0")/common.sh" >> "$OP/$L.s$N.meta"
cd "$W" || { echo "cd_failed" >> $OP/$L.s$N.meta; exit 0; }
PH=$(printf '%s' "$TXT" | sha256sum | cut -c1-64)
if [ "$N" = 1 ]; then echo "argv=$ENVI claude -p --session-id $SID $BASE $S1_TOOLS <prompt sha256:$PH>" >> $OP/$L.s$N.meta
else echo "argv=$ENVI claude -p --session-id $SID $BASE $S2_TOOLS --settings $S2_SETTINGS <prompt sha256:$PH>" >> $OP/$L.s$N.meta; fi
if [ "$N" = 1 ]; then $ENVI claude -p --session-id $SID $BASE $S1_TOOLS "$TXT" > $OP/$L.s1.jsonl 2> $OP/$L.s1.stderr
else $ENVI claude -p --session-id $SID $BASE $S2_TOOLS --settings "$S2_SETTINGS" "$TXT" > $OP/$L.s2.jsonl 2> $OP/$L.s2.stderr; fi
rc=$?; echo "exit=$rc" >> $OP/$L.s$N.meta; date -u +end=%FT%TZ >> $OP/$L.s$N.meta; exit 0
