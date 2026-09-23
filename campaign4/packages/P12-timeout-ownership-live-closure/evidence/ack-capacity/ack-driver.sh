#!/bin/bash
# P12-ack-capacity-1 ack driver, started by ackharness.sh in mode "acks" at the stall end. Real separate processes.
# Usage: ack-driver.sh BINARY WORKDIR OUTDIR. Writes OUTDIR/acks.log: one line per scenario event.
A_=$1; X=$2; OUT=$3; C="--config $X/fx.json"; ts() { date +%s.%N; }
L=$OUT/acks.log
det() { python - $X/fx.db $1 <<'PY'
import sqlite3, sys, json, datetime as D
try:
    c = sqlite3.connect('file:%s?mode=ro' % sys.argv[1], uri=True, timeout=0.2)
    p = json.loads(c.execute("select value from driver_kv where key=?", ('loop-pkg:' + sys.argv[2],)).fetchone()[0])
    t = p.get('timeout') or {}
    ts = [x for x in (t.get('at'), t.get('deferred_callback')) if x]
    print(min(D.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=D.timezone.utc).timestamp() for x in ts) if ts and p.get('step') == 'timed-out' else '')
except Exception: print('')
PY
}
waitdet() { until d=$(det $1); [ -n "$d" ]; do sleep 0.2; done; echo ${d%.*}; }
ack() { # name qid by next within submit_at [kill]
  local name=$1 q=$2 by=$3 next=$4 within=$5 at=$6 kill=${7:-}
  while [ $(date +%s) -lt $at ]; do sleep 0.05; done
  s=$(ts); $A_ timeout-ack $C --qid $q --action $q-w1 --by $by --next "$next" --within $within > $OUT/ack-$name.out 2>&1 & p=$!
  echo "$name submit qid=$q by=$by at=$s pid=$p detection=$(det $q) within=$within kill=${kill:-no}" >> $L
  if [ -n "$kill" ]; then until grep -q 'request recorded\|PENDING' $OUT/ack-$name.out 2>/dev/null || ! kill -0 $p 2>/dev/null; do sleep 0.01; done
    kill -9 $p 2>/dev/null; echo "$name requester SIGKILL at=$(ts) pid=$p" >> $L; fi
  wait $p; echo "$name rc=$? end=$(ts) out=$(tr '\n' ' ' < $OUT/ack-$name.out | cut -c1-240)" >> $L
}
d1=$(waitdet B01); ack timely      B01 fx-director "re-dispatch" 10m $((d1 + 5)) &
d2=$(waitdet B02); ack boundary    B02 fx-director "re-dispatch" 10m $((d2 + 34)) &
d3=$(waitdet B03); ack late        B03 fx-director "re-dispatch" 10m $((d3 + 62)) &
d4=$(waitdet B04); ack exit        B04 fx-director "re-dispatch" 10m $((d4 + 3)) kill &
d5=$(waitdet B05); ack dup-a       B05 fx-director "same" 10m $((d5 + 4)) & ack dup-b B05 fx-director "same" 10m $((d5 + 4)) &
d6=$(waitdet B06); ack conflict-a  B06 fx-director "first" 10m $((d6 + 6)) & ack conflict-b B06 fx-director "second" 10m $((d6 + 6)) &
d7=$(waitdet B07); ack forged      B07 fx-worker "take over" 10m $((d7 + 7)) &
d8=$(waitdet B08); ack expired     B08 fx-director "quick" 1s $((d8 + 8)) kill &
d10=$(waitdet B10); ack duty       B10 fx-duty "duty owns it" 10m $((d10 + 5)) &
# stopped run: stop run, then a request whose requester exits; only the outside check (every 30 s) can drain it
d9=$(waitdet B09); t=$((d9 + 70)); while [ $(date +%s) -lt $t ]; do sleep 0.1; done
$A_ stop $C > $OUT/stop.out 2>&1; echo "run-stop requested at=$(ts) rc=$?" >> $L
until ! kill -0 $(cat $X/run-current.pid) 2>/dev/null; do sleep 0.1; done; echo "run exited at=$(ts)" >> $L
p=$(det B09); ack stopped B09 fx-director "re-dispatch" 10m $(date +%s) kill
until ls $X/fx.db.acks/done/ 2>/dev/null | grep -q . && python - $X <<'PY'
import json, glob, sys
sys.exit(0 if any(json.load(open(f)).get('qid') == 'B09' for f in glob.glob(sys.argv[1] + '/fx.db.acks/done/*.json')) else 1)
PY
do sleep 0.5; done; echo "stopped drained at=$(ts)" >> $L
# restart run
rm -f $X/fx.db.stop; $A_ run $C --every 2s > $X/run3.out 2>&1 & echo $! > $X/run-current.pid; echo "run restarted pid=$(cat $X/run-current.pid) at=$(ts)" >> $L
wait
echo "driver done at=$(ts)" >> $L
