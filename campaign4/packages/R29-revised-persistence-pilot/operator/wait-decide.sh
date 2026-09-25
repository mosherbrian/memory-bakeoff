#!/bin/sh
# wait (max 30 min) until private package $1 is closed by the director
end=$(( $(date +%s) + 1800 ))
while [ $(date +%s) -lt $end ]; do
  s=$(/home/bmosher/.local/bin/agent-loop.prev-r23-47f69dfd status --config /home/bmosher/.config/agent-loop/campaign4-r29.json --json | python -c "import json,sys;print(next((p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'),'none'))")
  [ "$s" = closed ] && break; sleep 15
done
/home/bmosher/.local/bin/agent-loop.prev-r23-47f69dfd status --config /home/bmosher/.config/agent-loop/campaign4-r29.json | grep "$1"
