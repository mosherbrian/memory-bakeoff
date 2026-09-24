#!/bin/bash
# P13-receiver-binding-1: binding proofs. Real acp-worker runtime + passive engine + REAL wake (registry injected).
set -u
P=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership; S=$P/evidence/live-composition/stubs
. "$P/plans/receiver-eval.sh"
T=$(mktemp -d /tmp/p13rb-XXXX); export INJ=$T; n=0; bad=0
ok() { n=$((n+1)); echo "ok   $1"; }; no() { n=$((n+1)); bad=$((bad+1)); echo "FAIL $1"; }
E=$P/plans/passive-acp-engine.py
# 1. engine alone, NO AGENTDECK_INSTANCE_ID, HOME=A: records to the explicit path with the key
REC=$T/elsewhere/rec.jsonl
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' '{"jsonrpc":"2.0","id":2,"method":"session/new","params":{}}' '{"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"s","prompt":[{"type":"text","text":"nonce N1"}]}}' \
 | env -u AGENTDECK_INSTANCE_ID HOME=$T/homeA python3 "$E" "$REC" run1-director > $T/eng.out 2>&1
receiver_has "$REC" run1-director "nonce N1" && ok "engine without INSTANCE_ID records at the explicit path under its key" || no "engine did not record"
[ -z "$(ls $T/homeA/.local/share/p13-passive 2>/dev/null)" ] && ok "nothing written under HOME" || no "HOME-derived record"
# 2. fail closed
env -u AGENTDECK_INSTANCE_ID python3 "$E" < /dev/null > /dev/null 2>&1; [ $? = 2 ] && ok "engine without binding args exits 2" || no "engine ran unbound"
env -u AGENTDECK_INSTANCE_ID python3 "$E" relative/path k < /dev/null > /dev/null 2>&1; [ $? = 2 ] && ok "relative record path refused" || no "relative path accepted"
"$P/plans/acp-passive-lane" > /dev/null 2>&1; [ $? = 2 ] && ok "lane without binding args exits 2 before the runtime starts" || no "lane ran unbound"
[ -z "$(ls $T/*unknown* $T/homeA/.local/share/p13-passive/unknown.jsonl 2>/dev/null)" ] && ok "no unknown record anywhere" || no "unknown record exists"
# 3. composition: real acp-worker + lane with args, runtime instance id DIFFERENT from the key, HOME=B; wake with HOME=B
export HOME=$T/homeB; mkdir -p $HOME/.local/share/agent-deck
python3 -c "import json;json.dump([{'id':'rt-sid-77','title':'d','profile':'campaign4','status':'idle'}],open('$T/registry.json','w'))"
R2=$T/bound/director.jsonl
( sleep 60 | AGENTDECK_INSTANCE_ID=rt-sid-77 PATH=$S:/usr/bin:/bin "$P/plans/acp-passive-lane" "$R2" runX-director > $T/rt.out 2>&1 ) &
for i in $(seq 1 20); do [ -S "$HOME/.config/agent-deck/acp-sock/rt-sid-77.sock" ] && break; sleep 0.5; done
PATH=$S:/usr/bin:/bin AGENTDECK_PROFILE=campaign4 /var/home/bmosher/.config/agent-deck/wake rt-sid-77 "P13 passive receiver probe, run runX, nonce N2" > $T/w.out 2>&1; rc=$?
sleep 2
[ $rc = 0 ] && receiver_has "$R2" runX-director "nonce N2" && ok "real runtime + real wake: probe recorded at the bound path/key (runtime sid rt-sid-77 != key)" || no "composition probe not recorded (rc $rc)"
! grep -q "rt-sid-77" "$R2" && ok "record does not depend on the runtime instance id" || no "record keyed by the runtime id"
# 4. driver-side evaluation from a DIFFERENT HOME (C): independent of HOME
( HOME=$T/homeC; receiver_has "$R2" runX-director "nonce N2" ) && ok "evaluation from another HOME succeeds (binding is HOME-independent)" || no "HOME-dependent evaluation"
# 5. negatives
receiver_has "$R2" runX-duty "nonce N2" && no "NEG wrong key accepted" || ok "NEG wrong key refused"
receiver_has "$T/bound/other.jsonl" runX-director "nonce N2" && no "NEG wrong path accepted" || ok "NEG wrong path refused"
receiver_has "$R2" runX-director "nonce N3" && no "NEG stale/other nonce accepted" || ok "NEG stale nonce refused (only N2 recorded)"
receiver_has "bound/director.jsonl" runX-director "nonce N2" && no "NEG relative path accepted" || ok "NEG relative path refused"
for p in $(ps -eo pid=); do [ "$p" != $$ ] && grep -qa "INJ=$INJ" /proc/$p/environ 2>/dev/null && kill "$p" 2>/dev/null; done
echo "receiver-binding: $n checks, $bad wrong"; [ $bad -eq 0 ]
