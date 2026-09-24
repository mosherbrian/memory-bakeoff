#!/bin/bash
# P13 BINDING (read-only). Verifies the four prepared seats before the signature: exactly one registry
# row each, declared title, campaign4, not archived, status idle, a live worker socket, distinct from the
# main seats. Prints PASS or FAIL lines; rc 1 on any FAIL. Changes nothing.
set -u
. "$1"   # prep-result.env
export AGENTDECK_PROFILE=campaign4; bad=0
MAIN="0c933c75-1790000758 493c0317-1790000758 a79067ca-1790000758 56513e0e-1790000758"
reg=$(agent-deck list --json)
for k in W V D U; do n=${k}_NAME; i=${k}_ID; name=${!n}; id=${!i}
  case " $MAIN " in *" $id "*) echo "FAIL $id is a main seat"; bad=1; continue;; esac
  r=$(printf '%s' "$reg" | python3 -c 'import json,sys
d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get("sessions",[])
rows=[r for r in d if r.get("id")==sys.argv[1]]
if len(rows)!=1: print("rows=%d"%len(rows)); sys.exit()
r=rows[0]; print("ok" if r.get("title")==sys.argv[2] and r.get("profile","campaign4")=="campaign4" and not r.get("archived") and r.get("status") in ("idle","waiting") else "row %r"%{k:r.get(k) for k in ("title","profile","archived","status")})' "$id" "$name")
  s="$HOME/.config/agent-deck/acp-sock/$id.sock"
  if [ "$r" = ok ] && [ -S "$s" ]; then echo "PASS $k $name $id (socket $s)"; else echo "FAIL $k $name $id: registry $r, socket $([ -S "$s" ] && echo ok || echo missing)"; bad=1; fi
done
exit $bad
