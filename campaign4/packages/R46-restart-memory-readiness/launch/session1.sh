#!/bin/sh
# R46 session 1 (save). sh session1.sh WORKDIR PROMPTFILE OUTPREFIX
# No set -e: the claude exit code is captured and recorded even when nonzero.
set -u; W=$1; PROMPT=$2; O=$3
S1=$(python -c "import uuid;print(uuid.uuid4())"); echo "session_id=$S1" > $O.meta
cd "$W" || { echo "cd_failed" >> $O.meta; exit 2; }
env -i HOME=/var/home/bmosher PATH=/var/home/bmosher/.local/bin:/usr/bin:/bin \
  claude -p --session-id "$S1" --model claude-sonnet-5 --setting-sources project \
  --strict-mcp-config --disable-slash-commands --tools "Read,Write,Edit" --permission-mode acceptEdits \
  --output-format stream-json --verbose "$(cat "$PROMPT")" > $O.jsonl 2> $O.stderr
rc=$?; echo "exit=$rc" >> $O.meta; exit 0
