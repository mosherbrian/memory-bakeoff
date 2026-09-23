#!/bin/bash
# Real CLI, real time: a step timeout settles, `agent-loop stop` is in force (no run passes), nobody
# acknowledges; `agent-loop liveness` (the outside check) is run every 15 s for 150 s. Stub wake,
# agent-deck, systemctl (unit reported inactive/dead) and systemd-run. No real unit or seat.
# Usage: cli-stopped-noack.sh BINARY
set -u
A=$1; X=$(mktemp -d /tmp/p12-stop-noack-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
cat > $S/wake <<EOF
#!/bin/sh
echo "\$(date -u +%FT%TZ) \$1 \$(echo "\$2" | tr '\n' ' ' | head -c 160)" >> $X/wake.log
[ "\$2" = "/cancel" ] && { echo "wake: \$1 -> nothing running"; exit 1; }
echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\ncase "$*" in *show*) printf "ActiveState=inactive\\nSubState=dead\\nResult=success\\nNRestarts=0\\nInvocationID=\\nMainPID=0\\nExecMainStartTimestamp=\\n";; esac\n' > $S/systemctl
printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run
chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "agent-loop@fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"
echo "== $(sha256sum $A | cut -c1-16) workdir $X"
$A dispatch $C --qid L6b --worker fx-worker --verifier fx-verifier --task "no claim" --verify-task v --duration 5s --verify-window 5m >/dev/null 2>&1
$A run $C --once >/dev/null 2>&1
$A stop $C >/dev/null; echo "stop marker: $(ls $X/fx.db.stop 2>&1)"
sleep 7; cb=$(tail -1 $X/systemd-run.log | grep -o -- "timer-callback.*"); $A $cb > $X/cb.out 2>&1; echo "callback: $(head -c 100 $X/cb.out)"
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -le 150 ]; do
  out=$($A liveness $C 2>&1 | tail -1)
  echo "t+$(( $(date +%s) - t0 ))s liveness: $(echo "$out" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['verdict']['state'], 'alarm=%s' % d['verdict']['alarm'], [a for a in (d['actions'] or []) if 'timeout' in a])" 2>&1 | cut -c1-230)"
  sleep 15
done
echo "-- wakes:"; sed 's/^/   /' $X/wake.log | cut -c1-200
$A status $C --json | python3 -c "import json,sys; print('TIMEOUT', json.dumps([p['timeout'] for p in json.load(sys.stdin)['packages'] if p['qid']=='L6b'][0]))"
echo "-- liveness incident state: $(python3 -c "import json; d=json.load(open('$X/fx.db.liveness.json')); print('open incident:', d.get('open'))")"
