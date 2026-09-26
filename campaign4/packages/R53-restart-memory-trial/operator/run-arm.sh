#!/bin/sh
# R53 arm runner (R52 runner generalised by LABEL; R53 paths, R50 launcher/templates, R51 scanner+gate).
# Env overrides for offline preflight only: STUB_BIN (dir with a stub claude), GATE (gate script), OPDIR, DRY=1 (no wake/handoff).
set -u; L=$1; B=${L%-*}; A=${L#*-}
PK=/var/home/bmosher/memory-bake-off/campaign4/packages; R=$PK/R53-restart-memory-trial
OP=${OPDIR:-/tmp/campaign4-r53-op}/$L; GATE=${GATE:-$R/scanner/operator/scan_gate.py}; mkdir -p $OP; LOG=$OP/run.log
say() { echo "$(date -u +%FT%TZ) $L $*" >> $LOG; }
note() { [ "${DRY:-0}" = 1 ] || AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "$1" >/dev/null 2>&1; }
fail() { say "STOP: $*"; note "R53 operator STOP: $*. Evidence under $OP."; exit 1; }
LAUNCH=$R/launch
if [ -n "${STUB_BIN:-}" ]; then mkdir -p $OP/stublaunch; sed "s#PATH=/var/home/bmosher/.local/bin#PATH=$STUB_BIN#" $R/launch/common.sh > $OP/stublaunch/common.sh; cp $R/launch/session.sh $OP/stublaunch/; LAUNCH=$OP/stublaunch; fi
W=$(sh $R/launch/prep-arm.sh $L $B $OP); M=$(python -c "import json;print(json.load(open('$OP/$L.arm.json'))['memory'])")
[ -e "$M" ] && fail "memory store already exists ($M)"; [ -e "$(dirname $M)" ] && fail "project dir already exists"
echo 0 > $OP/calls
snap() { d=$OP/$L.mem-$1; mkdir -p $d; if [ -d "$M" ]; then cp -a "$M/." $d/; (cd $d && find . -type f | sort | xargs -r sha256sum) > $d.manifest; else echo ABSENT > $d.manifest; fi; }
timeout -k 15 180 sh $LAUNCH/session.sh 1 $L $OP $R/templates/session1-$A.txt; W1=$?; echo "wrapper_rc=$W1" >> $OP/$L.s1.meta; echo 1 > $OP/calls
C1=$(sed -n 's/^exit=//p' $OP/$L.s1.meta)
snap after-s1; snap before-s2
[ "$W1" = 0 ] && [ "$C1" = 0 ] || fail "session1 child exit=$C1 wrapper=$W1; no session2"
timeout -k 15 600 sh $LAUNCH/session.sh 2 $L $OP $R/templates/session2-$B.md; W2=$?; echo "wrapper_rc=$W2" >> $OP/$L.s2.meta; echo 2 > $OP/calls
C2=$(sed -n 's/^exit=//p' $OP/$L.s2.meta)
DENY="$(ls -d /tmp/c4x-* | grep -v "^$W" | tr '\n' ' ') $OP $PK"
python $GATE $OP/scan-gate-s1.json -- $OP/$L.s1.jsonl $W $M $DENY; G1=$?
python $GATE $OP/scan-gate-s2.json -- $OP/$L.s2.jsonl $W $M $DENY; G2=$?
python $PK/R42-benchmark-trace-repair/grade.py $W $OP/$L.oplog $(cat $W/bench.value) > $OP/grade-raw.json 2>&1
(cd $W && find . -type f | sort | xargs sha256sum) > $OP/arm-file-hashes.txt; cp -a $W $OP/arm-final
for g in $G1 $G2; do
  case $g in 0) ;; 5) echo "HOLD evaluator_failure" >> $OP/disposition.txt ;; *) echo "HOLD manual disposition required (gate $g)" >> $OP/disposition.txt ;; esac; done
[ "$W2" = 0 ] && [ "$C2" = 0 ] || echo "HOLD session2 child exit=$C2 wrapper=$W2" >> $OP/disposition.txt
say "done calls=$(cat $OP/calls) G1=$G1 G2=$G2 child=$C1/$C2 wrapper=$W1/$W2"
