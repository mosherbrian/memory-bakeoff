#!/bin/sh
# R67 runner: copy of R66 runner (paths only changed). R64 launch (copy of R56), R62 templates/fixture, R63 gate candidate, R51 scanner,
# R54 events.py. sh run-arm.sh LABEL   LABEL in {24576,12288}-{N,I,R} or D-{24576,12288}.
# Offline test seams (STUB_BIN, TEST_PROJECTS, TEST_PRECREATE, TEST_MUTATE_BETWEEN, TEST_TIMEOUT, GATE, EVENTS, OPROOT, EVIDENCE_DIR) are honoured ONLY when
# STUB_BIN is set, DRY=1, and STUB_BIN/claude is not the real claude; otherwise any seam variable aborts before any call.
set -u; LABEL=$1
PK=/var/home/bmosher/memory-bake-off/campaign4/packages
R56=$PK/R56-context-runner-readiness; R64=$PK/R72-prepared-offline-repair; G63=$PK/R72-prepared-offline-repair/operator/gate_r72.py
EV54=$PK/R54-memory-dependent-task-design/events.py
SEAMS="${TEST_PRECREATE:-}${TEST_MUTATE_BETWEEN:-}${TEST_PROJECTS:-}${TEST_TIMEOUT:-}${GATE:-}${EVENTS:-}${OPROOT:-}${EVIDENCE_DIR:-}"
if [ -n "${STUB_BIN:-}" ]; then
  [ "${DRY:-0}" = 1 ] || { echo "seam refused: STUB_BIN without DRY=1"; exit 3; }
  [ "$(realpath $STUB_BIN/claude)" != "$(realpath /var/home/bmosher/.local/bin/claude)" ] || { echo "seam refused: stub is real claude"; exit 3; }
else
  [ -z "$SEAMS" ] || { echo "seam refused: test variables set in live mode"; exit 3; }
fi
PROJECTS=${TEST_PROJECTS:-/var/home/bmosher/.claude/projects}; TO=${TEST_TIMEOUT:-timeout}
GATE=${GATE:-$R56/scanner/operator/scan_gate.py}; EVENTS=${EVENTS:-$EV54}
OPROOT=${OPROOT:-/tmp/campaign4-r72-op}; EVD=${EVIDENCE_DIR:-$R64/evidence}
case $LABEL in *-RD|*-ID|*-N) KIND=${LABEL#*-}; T=${LABEL%-*};; *) echo "bad label"; exit 2;; esac   # R71: prepared-memory kinds only, one session
[ -z "${STUB_BIN:-}" ] && [ "${R72_LIVE_RELEASE:-}" = "" ] && { echo "live refused: no R72 live release"; exit 3; }
LAUNCHMODE=live; [ -n "${STUB_BIN:-}" ] && LAUNCHMODE=stub
case $T in 24576|12288) ;; *) echo "bad target"; exit 2;; esac
# duplicate label: refuse before any side effect or call
[ -e $EVD/$LABEL ] && { echo "duplicate label $LABEL: bundle exists; zero calls"; exit 4; }
mkdir -p $OPROOT; HX() { python -c "import secrets;print(secrets.token_hex(6))"; }
OP=$OPROOT/o-$(HX); mkdir $OP; REGEN=0; W=/tmp/c4x-$(HX); while echo "$W" | grep -q "$T"; do REGEN=$((REGEN+1)); W=/tmp/c4x-$(HX); done; echo $REGEN > $OP/cwd-regenerations; [ -e $W ] && exit 1
echo 0 > $OP/calls
sh $R64/fixture/setup.sh $W $OP/log
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
  sh $R64/operator/freeze.sh $LABEL $OP $EVD
}
if [ -e "$PROJ" ] || [ -e "$M" ]; then hold "project or memory path exists before any call ($PROJ); zero calls"; finish; exit 1; fi
LAUNCH=$R64/launch; if [ -n "${STUB_BIN:-}" ]; then mkdir -p $OP/stublaunch; sed "s#PATH=/var/home/bmosher/.local/bin#PATH=$STUB_BIN#" $R64/launch/common.sh > $OP/stublaunch/common.sh; cp $R64/launch/session.sh $OP/stublaunch/; LAUNCH=$OP/stublaunch; fi
exitof() { v=$(sed -n 's/^exit=//p' $OP/arm.s$1.meta 2>/dev/null); [ -n "$v" ] && echo $v || echo MISSING; }
snap before-s1
# R71: seed the frozen prepared fixture (not natural saving), then zero-call fidelity preflight
FX=$R64/fixtures; case $KIND in RD) SRC=$FX/RD-$T;; ID) SRC=$FX/ID;; N) SRC=;; esac
[ -n "$SRC" ] && { mkdir -p $M; cp -a $SRC/. $M/; }
S2=$R64/templates/session2.md; sed "s#<CWD>#$W#g" $S2 > $OP/rendered-prompt.txt
LEAK=$(python - "$T" "$W" "$PROJ" "$M" "$OP/rendered-prompt.txt" "$W/bench.sh" "$KIND" <<'PYL'
import os,sys
T,W,PROJ,M,PR,B,K=sys.argv[1:8]; bad=[]
for name,val in (("cwd",W),("project",PROJ)):
    if T in val: bad.append(name)
for f in (PR,B):
    if T in open(f).read(): bad.append(os.path.basename(f))
if os.path.isdir(M):
    for fn in sorted(os.listdir(M)):
        if T in fn: bad.append("filename "+fn)
        if not (K=="RD" and fn=="bench-prefs.md") and T in open(os.path.join(M,fn)).read(): bad.append("content "+fn)
print(";".join(bad))
PYL
)
[ -n "$LEAK" ] && { hold "fidelity abort: target on participant-visible surface ($LEAK); zero calls"; snap before-s2; finish; exit 1; }
if false; then
  S1=$R64/templates/session1-$KIND.txt; [ $KIND = R ] && S1=$R64/templates/session1-R-$T.txt
  $TO -k 15 180 sh $LAUNCH/session.sh 1 arm $OP $S1; W1=$?; echo "wrapper_rc=$W1" >> $OP/arm.s1.meta; echo 1 > $OP/calls
  C1=$(exitof 1); snap after-s1
  if [ "$W1" != 0 ] || [ "$C1" != 0 ]; then hold "session1 child=$C1 wrapper=$W1; no session2"; finish; exit 1; fi
  [ -n "${STUB_BIN:-}" ] && [ -n "${TEST_MUTATE_BETWEEN:-}" ] && { mkdir -p $M; echo x > $M/injected.md; }   # offline-only
  snap before-s2; cmp -s $OP/mem-after-s1.manifest $OP/mem-before-s2.manifest && echo same > $OP/mem-compare || { echo DIFFERENT > $OP/mem-compare; hold "memory changed between sessions"; }
  S2=$R64/templates/session2.md
fi; snap before-s2
$TO -k 15 600 sh $LAUNCH/session.sh 2 arm $OP $S2; W2=$?; echo "wrapper_rc=$W2" >> $OP/arm.s2.meta
echo $(( $(cat $OP/calls) + 1 )) > $OP/calls; C2=$(exitof 2); snap after-s2
if [ "$W2" != 0 ] || [ "$C2" != 0 ]; then hold "session2 child=$C2 wrapper=$W2"; fi
DENY="$(ls -d /tmp/c4x-* | grep -v "^$W" | tr '\n' ' ') $OPROOT $PK"
for n in 1 2; do [ -f $OP/arm.s$n.jsonl ] || continue; python $GATE $OP/scan-gate-s$n.json -- $OP/arm.s$n.jsonl $W $M $DENY; g=$?; [ $g = 0 ] || hold "gate s$n=$g"; done
cp $W/report.md $OP/report.md 2>/dev/null
python $G63 $OP/log $T $OP/report.md > $OP/candidate-r63.json 2> $OP/candidate-r63.err
python -c "import json,sys;c=json.load(open('$OP/candidate-r63.json'))['candidate']['outcome'];sys.exit(1 if c in ('invalid_evidence','multi_context','schema_invalid','report_contradicts_log','manual_unresolved') else 0)" || hold "candidate $(python -c "import json;print(json.load(open('$OP/candidate-r63.json'))['candidate']['outcome'])" 2>/dev/null || echo FAILED)"
hold "awaiting adjudication"
python -c "import json,hashlib,re;h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest();s=lambda n:(re.findall(r'^session_id=(.*)$',open('$OP/arm.s%d.meta'%n).read(),re.M) or [None])[0] if __import__('os').path.exists('$OP/arm.s%d.meta'%n) else None;json.dump({'label':'$LABEL','kind':'$KIND','target':'$T','sessions':{'s1':s(1),'s2':s(2)},'runner_sha256':h('$R64/operator/run-arm.sh'),'gate_sha256':h('$G63'),'launch':'$LAUNCHMODE'},open('$OP/operator-meta.json','w'),indent=1)"
finish; echo "$LABEL $OP calls=$(cat $OP/calls)"
