#!/bin/bash
# P12-ack-capacity-1: pre-registered real-process runs (exact invocations).
set -u; H=$(cd $(dirname $0) && pwd)
NEW=~/projects/agent-loop-releases/agent-loop-269d6ee23f28/bin/agent-loop   # sha256 87e0905058ae5b21...
run() { name=$1; bin=$2; mode=$3; shift 3; ( env "$@" bash $H/ackharness.sh $bin $mode $H/$name > $H/$name.console 2>&1 ) & sleep 2; }
case $1 in
A) run ack-burst $NEW acks ARRIVE_FROM=end SLOW_ORDINARY=1 FAIL_EVERY=100000 TAIL=240 ;;
esac
wait
