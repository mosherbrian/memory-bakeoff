#!/bin/sh
# R45 session 1 (save). sh session1.sh ARM BLOCK   ARM in N|I|R. Operator-run; no participant chooses these flags.
# cwd = the arm's own directory, so Claude Code keeps this arm's auto-memory under ~/.claude/projects/<slug-of-cwd>/memory
# (existing Max login; no per-arm config dir, no credential copy).
set -eu; ARM=$1; BLOCK=$2; W=/tmp/campaign4-r45/arms/$BLOCK-$ARM; T=/var/home/bmosher/memory-bake-off/campaign4/packages/R44-restart-memory-design/templates
S1=$(python -c "import uuid;print(uuid.uuid4())"); echo "$S1" > $W.session1-id
cd $W
env -i HOME=/var/home/bmosher PATH=/var/home/bmosher/.local/bin:/usr/bin:/bin MODEL="$MODEL" claude -p --session-id "$S1" --model "$MODEL" --setting-sources project \
  --strict-mcp-config --disable-slash-commands --tools "Read Write Edit" \
  --output-format stream-json --verbose "$(cat $T/session1-$ARM.txt)" > $W.session1.jsonl
echo "exit=$?" >> $W.session1-id
