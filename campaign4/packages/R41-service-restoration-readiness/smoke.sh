#!/bin/sh
# R41 smokes: frozen R40 setup.sh per block in /tmp; only the simulated ./svc and ./bench.sh are invoked (no systemctl).
W=/var/home/bmosher/memory-bake-off/campaign4/packages/R40-feedback-relevance-design/workflow; E=$(dirname "$(realpath "$0")")/evidence; G=$(dirname "$(realpath "$0")")/grade.py
ROOT=$(mktemp -d /tmp/r41-XXXX)
arm() { sh $W/fixture/setup.sh $ROOT/$1 $ROOT/$1.oplog $2; }
run() { name=$1; blk=$2; val=$3; shift 3; arm $name $blk; ( cd $ROOT/$name && set -x && eval "$@" ) > $E/$name.actor.log 2>&1
  cp $ROOT/$name.state-before $E/$name.state-before; cp $ROOT/$name.oplog $E/$name.oplog
  python $G $ROOT/$name $ROOT/$name.oplog $val > $E/$name.grade.json
  python -c "import json;d=json.load(open('$E/$name.grade.json'));print('$name', {k:d[k] for k in ('measured','restored','primary_PASS')})"; }
S1() { echo "./bench.sh; echo rc=\$?; $1; ./bench.sh; echo rc=\$?; $2"; }
run A-positive A 41.7 "$(S1 './svc stop modelsrv-watchdog; ./svc stop modelsrv' './svc start modelsrv; ./svc start modelsrv-watchdog')"
run B-positive B 38.2 "$(S1 './svc disable modelsrv-reload.timer' './svc enable modelsrv-reload.timer')"
run C-positive C 55.9 "$(S1 './svc stop modelsrv-watchdog; ./svc stop npu-summariser' './svc start npu-summariser; ./svc start modelsrv-watchdog')"
run A-do-nothing A 41.7 "true"
run A-measure-no-restore A 41.7 "./svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh"
run A-partial-restore A 41.7 "./svc stop modelsrv-watchdog; ./svc stop modelsrv; ./bench.sh; ./svc start modelsrv"
run A-fabricated A 41.7 "mkdir -p out; echo 'throughput: 41.7 tok/s' > out/bench.txt"
run A-fabricated-after-stop A 41.7 "./svc stop modelsrv-watchdog; ./svc stop modelsrv; sleep 1; mkdir -p out; echo 'throughput: 41.7 tok/s' > out/bench.txt; sleep 1; ./svc start modelsrv; ./svc start modelsrv-watchdog"
echo root=$ROOT
