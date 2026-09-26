#!/bin/sh
# R53 per-release wrapper: reverify frozen pins and route, then run exactly one arm and hand it off. sh next-arm.sh LABEL
set -u; L=$1; R=/var/home/bmosher/memory-bake-off/campaign4/packages/R53-restart-memory-trial; cd $R
python - <<'PY' || { echo "PIN DRIFT - not running"; exit 1; }
import json, hashlib, sys
p = json.load(open("preparation-receipt.json"))["prepared_sha256"]
bad = [f for f, v in p.items() if not f.startswith("preflight/") and hashlib.sha256(open(f, "rb").read()).hexdigest() != v]
print("pins ok" if not bad else f"drift {bad}"); sys.exit(1 if bad else 0)
PY
env -i HOME=/var/home/bmosher PATH=/var/home/bmosher/.local/bin:/usr/bin:/bin claude auth status 2>/dev/null | python -c "import json,sys;d=json.load(sys.stdin);sys.exit(0 if (d.get('authMethod'),d.get('apiProvider'),d.get('subscriptionType'))==('claude.ai','firstParty','max') else 1)" || { echo "route not Max - not running"; exit 1; }
[ "$(ps -eo args | grep -c '[c]laude -p --session-id')" = 0 ] || { echo "competing participant - not running"; exit 1; }
[ -e /tmp/campaign4-r53-op/$L ] && { echo "arm $L already has an operator dir - not running"; exit 1; }
sh operator/run-arm.sh $L; echo "run rc=$?"; cat /tmp/campaign4-r53-op/$L/run.log; cat /tmp/campaign4-r53-op/$L/disposition.txt 2>/dev/null
sh operator/finish-arm.sh $L
