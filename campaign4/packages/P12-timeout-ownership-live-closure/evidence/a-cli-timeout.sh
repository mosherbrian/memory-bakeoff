#!/bin/bash
# A/B through the real CLI with the real wake reply shapes (wake exits 1 for every reply except
# started/queued; /cancel replies "cancelled" or "nothing running"). Stub wake, agent-deck,
# systemctl and systemd-run; no real unit, timer or seat. The deadline callback is run with the exact
# argv the timer was armed with, after its deadline.
# Usage: a-cli-timeout.sh BINARY idle|cancelled|refused
set -u
A=$1; MODE=$2; X=$(mktemp -d /tmp/p12-a-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
cat > $S/wake <<EOF
#!/bin/sh
echo "\$1 \$(echo "\$2" | tr '\n' ' ' | head -c 300)" >> $X/wake.log
if [ "\$2" = "/cancel" ]; then
  case $MODE in idle) echo "wake: \$1 -> nothing running"; exit 1;; cancelled) echo "wake: \$1 -> cancelled"; exit 1;;
    refused) echo "wake: could not reach \$1: [Errno 111] Connection refused" >&2; exit 1;; esac
fi
echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\necho "systemctl $*" >> %s/systemctl.log\n' $X > $S/systemctl
printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run
chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "agent-loop@fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"
step() { $A status $C --json 2>/dev/null | python3 -c "import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0])"; }
wk() { grep -c "^$1 " $X/wake.log; }
echo "== $(sha256sum $A | cut -c1-16) cancel reply: $MODE"
$A dispatch $C --qid L2 --worker fx-worker --verifier fx-verifier --task "no claim" --verify-task v --duration 5s --verify-window 5m >/dev/null 2>&1
echo "armed: $(tail -1 $X/systemd-run.log | cut -c1-140)"
sleep 7
cb=$(tail -1 $X/systemd-run.log | grep -o -- "timer-callback.*")
d0=$(wk D1); u0=$(wk U1)
$A $cb > $X/cb.out 2> $X/cb.err; echo "callback rc=$? stdout=$(head -c 200 $X/cb.out) stderr=$(head -c 200 $X/cb.err)"
echo "STEP=$(step L2) DIRECTOR_WAKES=$(( $(wk D1) - d0 )) DUTY_WAKES=$(( $(wk U1) - u0 ))"
echo "director notice: $(grep '^D1 ' $X/wake.log | tail -1 | cut -c1-300)"
$A status $C --json 2>/dev/null | python3 -c "import json,sys; print('TIMEOUT', json.dumps([p.get('timeout') for p in json.load(sys.stdin)['packages'] if p['qid']=='L2'][0]))"
echo "-- replay"; $A $cb > $X/cb2.out 2>&1; echo "replay rc=$? $(head -c 160 $X/cb2.out); director wakes now $(( $(wk D1) - d0 ))"
echo "-- ack"; $A timeout-ack $C --qid L2 --action L2-w1 --by fx-worker --next x --within 10m 2>&1 | head -2 | sed 's/^/   wrong actor: /'
$A timeout-ack $C --qid L2 --action L2-w1 --by fx-director --next "re-dispatch" --within 10m 2>&1 | head -2 | sed 's/^/   director: /'
$A timeout-ack $C --qid L2 --action L2-w1 --by fx-duty --next "other" --within 10m 2>&1 | head -2 | sed 's/^/   conflicting: /'
$A status $C --json 2>/dev/null | python3 -c "import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='L2'][0]; print('ACK', json.dumps((p.get('timeout') or {}).get('ack')), 'STEP', p['step'])"
