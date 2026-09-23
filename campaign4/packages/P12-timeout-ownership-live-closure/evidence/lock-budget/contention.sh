#!/bin/bash
# Real processes on one ledger: a running `run --every 2s`, 3 packages whose deadlines fall in the window,
# an ordinary dispatch every 4 s for ARRIVE_S s, and a SLOW transport (dispatch wakes take SLOW s; /cancel and
# notices are fast). Each deadline callback is run at its armed calendar instant (as systemd would), in its own
# process. Measures settlement lateness per deadline and (candidate) every lock hold from AGENT_LOOP_LOCK_LOG.
# Stubs only (wake, agent-deck, systemctl, systemd-run); no unit or seat. Usage: contention.sh BINARY [SLOW] [ARRIVE_S]
set -u
A_=$1; SLOW=${2:-20}; ARR=${3:-60}; X=$(mktemp -d /tmp/p12-cont-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
export AGENT_LOOP_LOCK_LOG=$X/lock.log
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
cat > $S/wake <<EOF
#!/bin/sh
t=\$(date +%s.%N)
case "\$2" in
  /cancel) echo "\$t \$1 cancel" >> $X/wake.log; echo "wake: \$1 -> nothing running"; exit 1;;
  '{"kind": "dispatch"'*) sleep $SLOW; echo "\$t \$1 dispatch(slow) done \$(date +%s.%N)" >> $X/wake.log;;
  *) echo "\$t \$1 notice \$(echo "\$2" | head -c 60)" >> $X/wake.log;;
esac
echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\nexit 0\n' > $S/systemctl; printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"; t0=$(date +%s)
echo "== $(sha256sum $A_ | cut -c1-16) slow=${SLOW}s arrivals=${ARR}s workdir $X"
$A_ run $C --every 2s > $X/run.out 2>&1 & PR=$!
for i in 1 2 3; do ( $A_ dispatch $C --qid T$i --worker fx-worker --verifier fx-verifier --task t --verify-task v --duration $((20 + 5*i))s --verify-window 5m > $X/dT$i.out 2>&1 ) & done
( n=0; while [ $(( $(date +%s) - t0 )) -lt $ARR ]; do n=$((n+1)); $A_ dispatch $C --qid O$n --worker fx-worker --verifier fx-verifier --task o --verify-task v --duration 10m --verify-window 5m >> $X/arrivals.out 2>&1 & sleep ${ARRIVE_EVERY:-4}; done; wait ) & PA=$!
# fire each T deadline callback at its armed calendar instant
for i in 1 2 3; do
  ( until grep -q "agent-loop-fx-T$i-w1.timer" $X/systemd-run.log 2>/dev/null; do sleep 0.2; done
    line=$(grep "agent-loop-fx-T$i-w1.timer" $X/systemd-run.log | head -1)
    at=$(echo "$line" | grep -o -- '--on-calendar=[^U]*UTC' | sed 's/--on-calendar=//'); ep=$(date -u -d "$at" +%s)
    while [ $(date +%s) -lt $ep ]; do sleep 0.1; done
    cb=$(echo "$line" | grep -o -- "timer-callback.*"); s=$(date +%s.%N)
    $A_ $cb > $X/cb-T$i.out 2>&1; echo "T$i deadline=$ep callback_start=$s callback_end=$(date +%s.%N) rc=$?" >> $X/callbacks.log ) &
done
sleep $((ARR + 45)); kill $PR 2>/dev/null; wait $PA 2>/dev/null; sleep 1
echo "-- callbacks:"; sort $X/callbacks.log | sed 's/^/   /'; for i in 1 2 3; do echo "   T$i out: $(tr '\n' ' ' < $X/cb-T$i.out | cut -c1-200)"; done
$A_ status $C --json 2>/dev/null | python3 -c "
import json, sys, datetime as D
cb = {l.split()[0]: dict(kv.split('=') for kv in l.split()[1:]) for l in open('$X/callbacks.log')}
for p in json.load(sys.stdin)['packages']:
    if not p['qid'].startswith('T'): continue
    t = p.get('timeout') or {}
    dl = float(cb.get(p['qid'], {}).get('deadline', 'nan'))
    at = D.datetime.fromisoformat(t['at'].replace('Z','+00:00')).timestamp() if t.get('at') else None
    print('SETTLE %s step=%s settled_after_deadline=%s lateness=%s deferred=%s' % (p['qid'], p['step'], None if at is None else round(at - dl, 1), t.get('callback_lateness'), t.get('deferred_callback')))
"
echo "arrivals dispatched: $(grep -c . $X/arrivals.out 2>/dev/null)"
if [ -s $X/lock.log ]; then python3 - $X/lock.log <<'PY'
import sys, collections
open_ = {}; holds = []
for l in open(sys.argv[1]):
    t, pid, ev, cmd = l.split()[0], l.split()[1], l.split()[2], (l.split()[3] if len(l.split()) > 3 else '')
    t = int(t) / 1e9
    if ev == 'acquire': open_[pid] = (t, cmd)
    elif pid in open_: s, c = open_.pop(pid); holds.append((t - s, c))
by = collections.defaultdict(list)
for d, c in holds: by[c].append(d)
print('LOCK holds: %d; MAX_HOLD=%.2fs; by command: %s' % (len(holds), max(d for d, _ in holds), {c: (len(v), round(max(v), 2)) for c, v in by.items()}))
PY
else echo "LOCK log: none (this build has no lock log)"; fi
echo "run output yields: $(grep -c 'yield' $X/run.out)"
