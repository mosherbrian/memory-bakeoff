#!/bin/sh
# R59 context-trial runner (R58 runner completed). Frozen dependencies used unchanged: R56 launcher/templates/fixture/
# scanner, R57 grader, R54 events.py. sh run-arm.sh LABEL   LABEL in {24576,12288}-{N,I,R} or D-{24576,12288}.
# Offline test seams (STUB_BIN, TEST_PROJECTS, TEST_PRECREATE, TEST_MUTATE_BETWEEN, TEST_TIMEOUT, GATE, EVENTS, OPROOT, EVIDENCE_DIR) are honoured ONLY when
# STUB_BIN is set, DRY=1, and STUB_BIN/claude is not the real claude; otherwise any seam variable aborts before any call.
set -u; LABEL=$1
PK=/var/home/bmosher/memory-bake-off/campaign4/packages
R56=$PK/R56-context-runner-readiness; R59=$PK/R59-context-readiness-completion
G57=$PK/R57-context-endpoint-repair/grade.py; EV54=$PK/R54-memory-dependent-task-design/events.py
SEAMS="${TEST_PRECREATE:-}${TEST_MUTATE_BETWEEN:-}${TEST_PROJECTS:-}${TEST_TIMEOUT:-}${GATE:-}${EVENTS:-}${OPROOT:-}${EVIDENCE_DIR:-}"
if [ -n "${STUB_BIN:-}" ]; then
  [ "${DRY:-0}" = 1 ] || { echo "seam refused: STUB_BIN without DRY=1"; exit 3; }
  [ "$(realpath $STUB_BIN/claude)" != "$(realpath /var/home/bmosher/.local/bin/claude)" ] || { echo "seam refused: stub is real claude"; exit 3; }
else
  [ -z "$SEAMS" ] || { echo "seam refused: test variables set in live mode"; exit 3; }
fi
PROJECTS=${TEST_PROJECTS:-/var/home/bmosher/.claude/projects}; TO=${TEST_TIMEOUT:-timeout}
GATE=${GATE:-$R56/scanner/operator/scan_gate.py}; EVENTS=${EVENTS:-$EV54}
OPROOT=${OPROOT:-/tmp/campaign4-r59-op}; EVD=${EVIDENCE_DIR:-$R59/evidence}
case $LABEL in D-*) KIND=D; T=${LABEL#D-};; *-N|*-I|*-R) KIND=${LABEL#*-}; T=${LABEL%-*};; *) echo "bad label"; exit 2;; esac
case $T in 24576|12288) ;; *) echo "bad target"; exit 2;; esac
# duplicate label: refuse before any side effect or call
[ -e $EVD/$LABEL ] && { echo "duplicate label $LABEL: bundle exists; zero calls"; exit 4; }
mkdir -p $OPROOT; HX() { python -c "import secrets;print(secrets.token_hex(6))"; }
OP=$OPROOT/o-$(HX); mkdir $OP; W=/tmp/c4x-$(HX); [ -e $W ] && exit 1
echo 0 > $OP/calls
sh $R56/fixture/setup.sh $W $OP/log
PROJ=$PROJECTS/$(echo $W | sed 's#[/.]#-#g'); M=$PROJ/memory
python -c "import json,os;json.dump({'cwd':'$W','cwd_real':os.path.realpath('$W'),'project':'$PROJ','project_real':os.path.realpath('$PROJ'),'memory':'$M','memory_real':os.path.realpath('$M')},open('$OP/paths.json','w'),indent=1)"
echo "{\"cwd\":\"$W\",\"memory\":\"$M\"}" > $OP/arm.arm.json
echo "{\"label\":\"$LABEL\",\"target\":\"$T\",\"kind\":\"$KIND\",\"op\":\"$OP\",\"cwd\":\"$W\"}" >> $OPROOT/map.jsonl
hold() { echo "HOLD $*" >> $OP/disposition.txt; }
[ -n "${STUB_BIN:-}" ] && case "${TEST_PRECREATE:-}" in project) mkdir -p $PROJ;; memory) mkdir -p $M;; esac   # offline-only
snap() { d=$OP/mem-$1; mkdir -p $d; if [ -d "$M" ]; then cp -a "$M/." $d/; (cd $d && find . -type f | sort | xargs -r sha256sum) > $d.manifest; [ -s $d.manifest ] || echo EMPTY_DIR > $d.manifest; else echo ABSENT > $d.manifest; fi; }
finish() {   # every exit path: simulator copy, events, freeze
  [ -d $W ] && cp -a $W $OP/arm-final || echo "simulator missing" > $OP/arm-final.MISSING
  for n in 1 2; do
    if [ -f $OP/arm.s$n.jsonl ]; then
      python $EVENTS $OP/arm.s$n.jsonl $M $OP/mem-before-s$n.manifest > $OP/events-s$n.json 2> $OP/events-s$n.err \
        && python -c "import json,sys;d=json.load(open('$OP/events-s$n.json'));sys.exit(1 if any(k in d['counts'] for k in ('unresolved','unsupported_shell','denied')) else 0)" \
        || { python -c "import json;json.load(open('$OP/events-s$n.json'))" 2>/dev/null && hold "events s$n: unresolved/unsupported/denied memory events (manual)" || hold "events s$n: evaluator failure"; }
    fi; done
  sh $R59/operator/freeze.sh $LABEL $OP $EVD
}
if [ -e "$PROJ" ] || [ -e "$M" ]; then hold "project or memory path exists before any call ($PROJ); zero calls"; finish; exit 1; fi
LAUNCH=$R56/launch; if [ -n "${STUB_BIN:-}" ]; then mkdir -p $OP/stublaunch; sed "s#PATH=/var/home/bmosher/.local/bin#PATH=$STUB_BIN#" $R56/launch/common.sh > $OP/stublaunch/common.sh; cp $R56/launch/session.sh $OP/stublaunch/; LAUNCH=$OP/stublaunch; fi
exitof() { v=$(sed -n 's/^exit=//p' $OP/arm.s$1.meta 2>/dev/null); [ -n "$v" ] && echo $v || echo MISSING; }
snap before-s1
if [ $KIND != D ]; then
  S1=$R56/templates/session1-$KIND.txt; [ $KIND = R ] && S1=$R56/templates/session1-R-$T.txt
  $TO -k 15 180 sh $LAUNCH/session.sh 1 arm $OP $S1; W1=$?; echo "wrapper_rc=$W1" >> $OP/arm.s1.meta; echo 1 > $OP/calls
  C1=$(exitof 1); snap after-s1
  if [ "$W1" != 0 ] || [ "$C1" != 0 ]; then hold "session1 child=$C1 wrapper=$W1; no session2"; finish; exit 1; fi
  [ -n "${STUB_BIN:-}" ] && [ -n "${TEST_MUTATE_BETWEEN:-}" ] && { mkdir -p $M; echo x > $M/injected.md; }   # offline-only
  snap before-s2; cmp -s $OP/mem-after-s1.manifest $OP/mem-before-s2.manifest && echo same > $OP/mem-compare || { echo DIFFERENT > $OP/mem-compare; hold "memory changed between sessions"; }
  S2=$R56/templates/session2.md
else snap before-s2; S2=$R56/templates/D-$T.md; fi
$TO -k 15 600 sh $LAUNCH/session.sh 2 arm $OP $S2; W2=$?; echo "wrapper_rc=$W2" >> $OP/arm.s2.meta
echo $(( $(cat $OP/calls) + 1 )) > $OP/calls; C2=$(exitof 2); snap after-s2
if [ "$W2" != 0 ] || [ "$C2" != 0 ]; then hold "session2 child=$C2 wrapper=$W2"; fi
DENY="$(ls -d /tmp/c4x-* | grep -v "^$W" | tr '\n' ' ') $OPROOT $PK"
for n in 1 2; do [ -f $OP/arm.s$n.jsonl ] || continue; python $GATE $OP/scan-gate-s$n.json -- $OP/arm.s$n.jsonl $W $M $DENY; g=$?; [ $g = 0 ] || hold "gate s$n=$g"; done
python $G57 $OP/log $T $W/report.md > $OP/grade-r57.json 2>&1
python -c "import json,sys;d=json.load(open('$OP/grade-r57.json'));sys.exit(1 if d['manual'] else 0)" || hold "R57 manual adjudication"
finish; echo "$LABEL $OP calls=$(cat $OP/calls)"
