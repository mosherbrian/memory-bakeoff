#!/bin/sh
# R45 session 2 (task). New process, new session id, never --resume/--continue. sh session2.sh ARM BLOCK
set -eu; ARM=$1; BLOCK=$2; W=/tmp/campaign4-r45/arms/$BLOCK-$ARM; TASK=/var/home/bmosher/memory-bake-off/campaign4/packages/R45-restart-isolation-repair/tasks/$BLOCK-common.md
S2=$(python -c "import uuid;print(uuid.uuid4())"); echo "$S2" > $W.session2-id
cd $W
claude -p --session-id "$S2" --model "$MODEL" --setting-sources project \
  --strict-mcp-config --disable-slash-commands --tools "Bash Read Write" \
  --settings '{"permissions":{"allow":["Bash(./svc:*)","Bash(./bench.sh)"],"deny":["Bash(systemctl:*)"]}}' \
  --output-format stream-json --verbose "$(sed "s/<ARM>/$ARM/g" $TASK)" > $W.session2.jsonl
echo "exit=$?" >> $W.session2-id
