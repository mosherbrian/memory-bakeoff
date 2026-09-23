#!/bin/bash
# P12-fair-handoff-1: the pre-registered real-process runs (exact invocations). Batch A = new release, batch B = old.
# Usage: run-all.sh A|B      Each run writes <name>/workload.json before any process starts.
set -u; H=$(cd $(dirname $0) && pwd)
NEW=~/projects/agent-loop-releases/agent-loop-1d63b77517e0/bin/agent-loop   # sha256 a41e7b71de050199...
OLD=~/projects/agent-loop-releases/agent-loop-487cb92ce9d3/bin/agent-loop   # sha256 b70665f5...
MIX="FAIL_EVERY=7 QUEUED_EVERY=5 HANG_EVERY=11 FAIL_FIRST_DUTY=1"
run() { name=$1; bin=$2; mode=$3; shift 3; ( env "$@" bash $H/fairhandoff.sh $bin $mode $H/$name > $H/$name.console 2>&1 ) & sleep 2; }
case $1 in
A) run new-supported $NEW drain ARRIVE_FROM=end SLOW_ORDINARY=0 $MIX
   run new-overload  $NEW drain ARRIVE_FROM=stall SLOW_ORDINARY=1 ARRIVE_EVERY=4 $MIX
   run new-crash2    $NEW crash2 ARRIVE_FROM=end SLOW_ORDINARY=1 FAIL_EVERY=100000 ;;
B) run old-overload  $OLD drain ARRIVE_FROM=stall SLOW_ORDINARY=1 ARRIVE_EVERY=4 $MIX
   run old-crash2    $OLD crash2 ARRIVE_FROM=end SLOW_ORDINARY=1 FAIL_EVERY=100000 ;;
esac
wait
