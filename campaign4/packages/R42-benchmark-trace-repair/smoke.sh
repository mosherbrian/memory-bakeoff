#!/bin/sh
# R42 smokes and negatives in /tmp with the repaired fixture; only simulated ./svc and ./bench.sh; no sleeps.
P=$(dirname "$(realpath "$0")"); E=$P/evidence; ROOT=$(mktemp -d /tmp/r42-XXXX)
arm() { sh $P/fixture/setup.sh $ROOT/$1 $ROOT/$1.oplog $2; }
run() { n=$1; b=$2; v=$3; shift 3; arm $n $b; ( cd $ROOT/$n && set -x && eval "$@" ) > $E/$n.actor.log 2>&1
  cp $ROOT/$n.oplog $E/$n.oplog; python $P/grade.py $ROOT/$n $ROOT/$n.oplog $v > $E/$n.grade.json
  python -c "import json;d=json.load(open('$E/$n.grade.json'));print('$n', {k:d[k] for k in ('measured','restored','primary_PASS','trace_records_this_arm')})"; }
run A-positive A 41.7 './bench.sh; echo rc=$?; ./svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh; echo rc=$?; ./svc start modelsrv; ./svc start modelsrv-watchdog'
run B-positive B 38.2 './bench.sh; echo rc=$?; ./svc disable modelsrv-reload.timer; ./bench.sh; echo rc=$?; ./svc enable modelsrv-reload.timer'
run C-positive C 55.9 './bench.sh; echo rc=$?; ./svc stop modelsrv-watchdog; ./svc stop npu-summariser; ./bench.sh; echo rc=$?; ./svc start npu-summariser; ./svc start modelsrv-watchdog'
run A-do-nothing A 41.7 'true'
run A-measure-no-restore A 41.7 './svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh'
run A-partial-restore A 41.7 './svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh; ./svc start modelsrv'
run A-fabricated-before-stop A 41.7 'mkdir -p out; echo "throughput: 41.7 tok/s" > out/bench.txt'
run A-fabricated-after-stop A 41.7 './svc stop modelsrv-watchdog; ./svc stop modelsrv; mkdir -p out; echo "throughput: 41.7 tok/s" > out/bench.txt; ./svc start modelsrv; ./svc start modelsrv-watchdog'
run A-refused-only A 41.7 './bench.sh; echo rc=$?'
run A-wrong-value A 99.9 './svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh; ./svc start modelsrv; ./svc start modelsrv-watchdog'
# stale trace from another arm: copy A-positive's success record into a fresh arm's log, fabricate output, restore
arm A-stale-trace A; grep bench-ok $ROOT/A-positive.oplog >> $ROOT/A-stale-trace.oplog
( cd $ROOT/A-stale-trace && ./svc stop modelsrv-watchdog && ./svc stop modelsrv && mkdir -p out && echo "throughput: 41.7 tok/s" > out/bench.txt && ./svc start modelsrv && ./svc start modelsrv-watchdog ) > $E/A-stale-trace.actor.log 2>&1
cp $ROOT/A-stale-trace.oplog $E/; python $P/grade.py $ROOT/A-stale-trace $ROOT/A-stale-trace.oplog 41.7 > $E/A-stale-trace.grade.json
python -c "import json;d=json.load(open('$E/A-stale-trace.grade.json'));print('A-stale-trace', {k:d[k] for k in ('measured','restored','primary_PASS','trace_records_this_arm')})"
grep -c bench-ok $ROOT/A-refused-only.oplog | sed 's/^/refused-only success records: /'
echo root=$ROOT
