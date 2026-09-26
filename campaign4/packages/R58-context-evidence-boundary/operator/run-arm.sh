#!/bin/sh
# R58 context-trial runner = R56 runner + memory snapshots, all child/wrapper checks, authoritative R57 grade, immutable bundle.
# R56 components (launcher, templates, fixture, scanner) are used unchanged from the R56 package. sh run-arm.sh LABEL   LABEL in {24576,12288}-{N,I,R} or D-{24576,12288}
# Participant-visible paths are opaque: cwd /tmp/c4x-<12 hex> and operator log /tmp/campaign4-r56-op/o-<12 hex>/log.
# The label->id/target mapping lives only in $OPROOT/map.jsonl (outside the cwd; the scan gate denies $OPROOT).
# Env for offline checks only: STUB_BIN, GATE, OPROOT, DRY=1.
set -u; LABEL=$1; R=/var/home/bmosher/memory-bake-off/campaign4/packages/R56-context-runner-readiness; R58=/var/home/bmosher/memory-bake-off/campaign4/packages/R58-context-evidence-boundary; G57=/var/home/bmosher/memory-bake-off/campaign4/packages/R57-context-endpoint-repair/grade.py
OPROOT=${OPROOT:-/tmp/campaign4-r58-op}; mkdir -p $OPROOT; GATE=${GATE:-$R/scanner/operator/scan_gate.py}
case $LABEL in D-*) KIND=D; T=${LABEL#D-};; *-N|*-I|*-R) KIND=${LABEL#*-}; T=${LABEL%-*};; *) echo "bad label"; exit 2;; esac
case $T in 24576|12288) ;; *) echo "bad target"; exit 2;; esac
# opaque ids are lowercase hex only, so no random suffix can look like a label (-N/-I/-R/D-) or a target
HX() { python -c "import secrets;print(secrets.token_hex(6))"; }
OP=$OPROOT/o-$(HX); mkdir $OP; W=/tmp/c4x-$(HX); [ -e $W ] && exit 1
sh $R/fixture/setup.sh $W $OP/log
M=/var/home/bmosher/.claude/projects/$(echo $W | sed 's#[/.]#-#g')/memory
echo "{\"cwd\":\"$W\",\"memory\":\"$M\"}" > $OP/arm.arm.json
echo "{\"label\":\"$LABEL\",\"target\":\"$T\",\"kind\":\"$KIND\",\"op\":\"$OP\",\"cwd\":\"$W\"}" >> $OPROOT/map.jsonl
[ -e "$M" ] && { echo "memory exists: $M" > $OP/HOLD; exit 1; }
LAUNCH=$R/launch; if [ -n "${STUB_BIN:-}" ]; then mkdir -p $OP/stublaunch; sed "s#PATH=/var/home/bmosher/.local/bin#PATH=$STUB_BIN#" $R/launch/common.sh > $OP/stublaunch/common.sh; cp $R/launch/session.sh $OP/stublaunch/; LAUNCH=$OP/stublaunch; fi
snap() { d=$OP/mem-$1; mkdir -p $d; if [ -d "$M" ]; then cp -a "$M/." $d/; (cd $d && find . -type f | sort | xargs -r sha256sum) > $d.manifest; else echo ABSENT > $d.manifest; fi; }
snap before-s1
calls=0
if [ $KIND != D ]; then
  S1=$R/templates/session1-$KIND.txt; [ $KIND = R ] && S1=$R/templates/session1-R-$T.txt
  timeout -k 15 180 sh $LAUNCH/session.sh 1 arm $OP $S1; W1=$?; echo "wrapper_rc=$W1" >> $OP/arm.s1.meta; calls=1
  C1=$(sed -n 's/^exit=//p' $OP/arm.s1.meta); snap after-s1
  [ "$W1" = 0 ] && [ "$C1" = 0 ] || { echo "session1 exit=$C1 wrapper=$W1; no session2" > $OP/HOLD; echo $calls > $OP/calls; sh $R58/operator/freeze.sh $LABEL $OP; exit 1; }
  snap before-s2; cmp -s $OP/mem-after-s1.manifest $OP/mem-before-s2.manifest && echo same > $OP/mem-compare || echo DIFFERENT > $OP/mem-compare
  S2=$R/templates/session2.md
else S2=$R/templates/D-$T.md; fi
timeout -k 15 600 sh $LAUNCH/session.sh 2 arm $OP $S2; W2=$?; echo "wrapper_rc=$W2" >> $OP/arm.s2.meta; calls=$((calls+1)); echo $calls > $OP/calls; snap after-s2
C2=$(sed -n 's/^exit=//p' $OP/arm.s2.meta); [ "$W2" = 0 ] && [ "$C2" = 0 ] || echo "HOLD session2 exit=$C2 wrapper=$W2" >> $OP/disposition.txt
DENY="$(ls -d /tmp/c4x-* | grep -v "^$W" | tr '\n' ' ') $OPROOT /var/home/bmosher/memory-bake-off/campaign4/packages"
for n in 1 2; do [ -f $OP/arm.s$n.jsonl ] || continue; python $GATE $OP/scan-gate-s$n.json -- $OP/arm.s$n.jsonl $W $M $DENY; g=$?
  [ $g = 0 ] || echo "HOLD gate s$n=$g (manual disposition)" >> $OP/disposition.txt; done
python $G57 $OP/log $T $W/report.md > $OP/grade-r57.json 2>&1   # authoritative (R57); manual=true requires adjudication
python -c "import json,sys;d=json.load(open('$OP/grade-r57.json'));sys.exit(0 if not d['manual'] else 1)" || echo "HOLD manual adjudication (R57 manual=true)" >> $OP/disposition.txt
cp -a $W $OP/arm-final
sh $R58/operator/freeze.sh $LABEL $OP
echo "$LABEL $OP calls=$calls"
