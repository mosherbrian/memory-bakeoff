#!/bin/bash
# One dispatch (a lock holder) whose wake send takes SLOW s; a second writer (timeout-ack attempt on an unknown
# package, which only needs the lock) starts 1 s later and records how long it waited. Old build: the hold grows
# with the send (transport timeout 30 s); new build: the hold is capped by the 10 s budget. Usage: hold-scaling.sh BINARY SLOW
set -u
A_=$1; SLOW=$2; X=$(mktemp -d /tmp/p12-hold-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
printf '#!/bin/sh\nsleep %s\necho "wake: $1 -> started"\n' $SLOW > $S/wake; printf '#!/bin/sh\nexit 0\n' > $S/systemctl; printf '#!/bin/sh\nexit 0\n' > $S/systemd-run; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
t0=$(date +%s.%N)
$A_ dispatch --config $X/fx.json --qid Q --worker fx-worker --verifier fx-verifier --task t --verify-task v --duration 10m --verify-window 5m > $X/d.out 2>&1 &
sleep 1; t1=$(date +%s.%N)
$A_ timeout-ack --config $X/fx.json --qid none --action none --by fx-director --next x --within 1m > $X/a.out 2>&1; t2=$(date +%s.%N)
wait; t3=$(date +%s.%N)
python3 -c "print('== $(sha256sum $A_ | cut -c1-16) slow=${SLOW}s: dispatch (holder) took %.1f s; second writer waited %.1f s for the lock' % ($t3-$t0, $t2-$t1))"
echo "   dispatch: $(tr '\n' ' ' < $X/d.out | cut -c1-140)"
