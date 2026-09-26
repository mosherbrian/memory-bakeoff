#!/bin/sh
# sh prep-arm.sh LABEL BLOCK OPDIR -> creates an opaque cwd /tmp/c4x-XXXXXXXX with the R42 simulated fixture;
# records LABEL->cwd, the operator log path and state-before in OPDIR (never inside the arm).
set -u; L=$1; B=$2; OP=$3; mkdir -p $OP; W=$(mktemp -d /tmp/c4x-XXXXXXXX); rmdir $W
sh /var/home/bmosher/memory-bake-off/campaign4/packages/R42-benchmark-trace-repair/fixture/setup.sh $W $OP/$L.oplog $B > /dev/null
cp $W.state-before $OP/$L.state-before   # grade.py reads ARMDIR.state-before (sibling, outside the arm)
echo "{\"label\":\"$L\",\"block\":\"$B\",\"cwd\":\"$W\",\"memory\":\"/var/home/bmosher/.claude/projects/$(echo $W | sed 's#[/.]#-#g')/memory\"}" > $OP/$L.arm.json
echo $W
