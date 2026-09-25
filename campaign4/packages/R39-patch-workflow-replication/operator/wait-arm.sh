#!/bin/sh
# wait until private package $1 leaves the worker/verify steps (max 20 min), then print its status line
end=$(( $(date +%s) + 1200 ))
while [ $(date +%s) -lt $end ]; do
  s=$(/home/bmosher/.local/bin/agent-loop status --config /home/bmosher/.config/agent-loop/campaign4.json --json | python -c "import json,sys;print(next((p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'),'none'))")
  case "$s" in worker|verify) sleep 15;; *) break;; esac
done
/home/bmosher/.local/bin/agent-loop status --config /home/bmosher/.config/agent-loop/campaign4.json | grep "$1"
