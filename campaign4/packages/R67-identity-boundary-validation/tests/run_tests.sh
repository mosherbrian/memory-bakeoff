#!/bin/sh
# R67 offline suite (R66 regressions + R67 content cases): actual copied runner/freeze/finalizer with stubs; fresh ROOT per run; native roots untouched.
R=$(cd "$(dirname "$0")/.." && pwd); ROOT=${1:?root}; mkdir -p $ROOT; S=$R/tests/stubs; RES=$ROOT/results.txt; : > $RES
FZ=$R/operator/freeze.sh; FN=$R/operator/finalize.py; export R67_TEST_PROJECTS=/tmp/r67-fp
run() { E=$1; L=$2; shift 2; env DRY=1 TEST_PROJECTS=/tmp/r67-fp OPROOT=$ROOT/op-$(basename $E) EVIDENCE_DIR=$E "$@" sh $R/operator/run-arm.sh $L > $ROOT/out-$(basename $E)-$L 2>&1; }
fin() { python $FN "$2" "$3" "$1" "$4" > $ROOT/fin.json; rc=$?; python -c "import json;d=json.load(open('$ROOT/fin.json'));print('rc=$rc',d['status'],d['final_primary'],d.get('final_outcome'),'term='+str(d.get('terminal_written','-')),'|',d['reason'][:60])"; }
rec() { python - "$@" <<'PY'
import json,hashlib,sys
ev,lab,out,kind=sys.argv[1:5]; a=f"{ev}/{lab}"; h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest(); c=json.load(open(a+"/candidate-r63.json"))["candidate"]
r={"TEST_ONLY":"offline stub receipt, not an independent review","schema":"r63-adjudication-v1","label":lab,"arm_claim_sha256":h(a+"/arm-claim.json"),"reviewer":"corvid-TESTSTUB",
 "log_sha256":c["log_sha256"],"report_sha256":c["report_sha256"] if kind!="stale" else "0"*64,"candidate_outcome":c["outcome"],"decision":"reject" if kind=="reject" else "approve","guessing":False,"contradiction":False,
 "reason":"test","source_evidence":"indeterminate" if kind=="srcind" else "observed","ask_relevant":"yes" if c["outcome"]=="asked_no_run" else "not_applicable"}
json.dump(r,open(out,"w"),indent=1)
PY
}
EV=$ROOT/ev; FD=$ROOT/fin
for L in 24576-N 12288-R 24576-I 12288-N 24576-R 12288-I D-12288 D-24576; do run $EV $L STUB_BIN=$S/work; A=$EV/$L
  echo "U1 $L calls=$(cat $A/calls) cand=$(python -c "import json;print(json.load(open('$A/candidate-r63.json'))['candidate']['outcome'])") mem_after_s1=$(head -c 6 $A/mem-after-s1.manifest 2>/dev/null || echo -) disp=[$(tr '\n' ';' < $A/disposition.txt)]" >> $RES; done
H0=$(cd $EV && find . -type f | sort | xargs sha256sum | sha256sum)
echo "U2 no receipt: $(fin $EV 24576-R - $FD)" >> $RES
rec $EV 24576-R $ROOT/ok-24576-R.json ok; echo "U2 then valid approve: $(fin $EV 24576-R $ROOT/ok-24576-R.json $FD) attempts=$(ls $FD/24576-R/attempts | wc -l)" >> $RES
rec $EV 12288-R $ROOT/st.json stale; echo "U3 stale: $(fin $EV 12288-R $ROOT/st.json $FD)" >> $RES
rec $EV 12288-R $ROOT/ok-12288-R.json ok; echo "U3 then valid: $(fin $EV 12288-R $ROOT/ok-12288-R.json $FD)" >> $RES
T0=$(sha256sum $FD/24576-R/terminal.json); echo "U4 second valid: $(fin $EV 24576-R $ROOT/ok-24576-R.json $FD) terminal_unchanged=$([ "$T0" = "$(sha256sum $FD/24576-R/terminal.json)" ] && echo yes || echo NO)" >> $RES
rec $EV D-24576 $ROOT/ok-D.json ok; for i in 1 2 3 4; do python $FN D-24576 $ROOT/ok-D.json $EV $FD > $ROOT/conc-$i.json & done; wait
echo "U5 concurrent x4: terminals=$(ls $FD/D-24576/terminal.json | wc -l) written=$(grep -l '"terminal_written": true' $ROOT/conc-*.json | wc -l) attempts=$(ls $FD/D-24576/attempts | wc -l)" >> $RES
rec $EV 24576-I $ROOT/rej.json reject; echo "U12 reject: $(fin $EV 24576-I $ROOT/rej.json $FD)" >> $RES
rec $EV D-12288 $ROOT/si.json srcind; echo "U12 source indeterminate: $(fin $EV D-12288 $ROOT/si.json $FD)" >> $RES
echo "U10 cross-arm receipt: $(fin $EV 12288-N $ROOT/ok-24576-R.json $FD)" >> $RES
# U6/U7: remove or break status evidence in an op-dir copy BEFORE freeze, freeze to a separate evidence dir
OPD=$(python -c "import json;[print(json.loads(l)['op']) for l in open('$ROOT/op-ev/map.jsonl') if json.loads(l)['label']=='24576-N']")
for c in "disp:rm disposition.txt" "events:malformed events-s2.json" "scan:rm scan-gate-s2.json" "wrapper:dropline arm.s2.meta"; do n=${c%%:*}; act=${c#*:}; op=${act%% *}; f=${act#* }
  C=$ROOT/opcopy-$n; cp -a $OPD $C; case $op in rm) rm $C/$f;; malformed) printf '{bad' > $C/$f;; dropline) sed -i '/^wrapper_rc=/d' $C/$f;; esac
  E=$ROOT/ev-pre-$n; sh $FZ 24576-N $C $E >/dev/null 2>&1; rec $E 24576-N $ROOT/r-$n.json ok 2>/dev/null
  echo "U6/7 $n before freeze (missing=$(python -c "import json;print(json.load(open('$E/24576-N/arm-claim.json'))['missing'])")): $(fin $E 24576-N $ROOT/r-$n.json $ROOT/fin-$n)" >> $RES; done
# U8 infra failures with approve receipt
for c in "s1fail 24576-R STUB_BIN=$S/s1fail" "s2fail 12288-R STUB_BIN=$S/s2fail" "gate1 24576-I STUB_BIN=$S/work GATE=$S/gate1.py" "evfail 12288-I STUB_BIN=$S/work EVENTS=$S/ev_fail.py" "mutate 24576-R STUB_BIN=$S/work TEST_MUTATE_BETWEEN=1"; do
  set -- $c; n=$1; L=$2; shift 2; E=$ROOT/ev-$n; run $E $L "$@"; rec $E $L $ROOT/r-$n.json ok 2>/dev/null
  echo "U8 $n: $(fin $E $L $ROOT/r-$n.json $ROOT/fin-$n)" >> $RES; done
# U9 finalizer dependency hash changed in claim; U11 tamper
T=$ROOT/tamp-dep; mkdir -p $T; cp -a $EV/24576-R $T/; python -c "
import json;p='$T/24576-R/arm-claim.json';c=json.load(open(p));k=[x for x in c['dependency_sha256'] if x.endswith('finalize.py')][0];c['dependency_sha256'][k]='0'*64;json.dump(c,open(p,'w'))"
rec $T 24576-R $ROOT/r-dep.json ok; echo "U9 finalizer dep hash changed: $(fin $T 24576-R $ROOT/r-dep.json $ROOT/fin-dep)" >> $RES
for f in log report.md arm.s2.jsonl; do T=$ROOT/tamp-$(echo $f|tr . _); mkdir -p $T; cp -a $EV/24576-R $T/; printf x >> $T/24576-R/$f; echo "U11 tampered $f: $(fin $T 24576-R $ROOT/ok-24576-R.json $ROOT/fin-t$f)" >> $RES; done
H1=$(cd $EV && find . -type f | sort | xargs sha256sum | sha256sum); echo "U14 bundles unchanged after finalization: $([ "$H0" = "$H1" ] && echo yes || echo NO)" >> $RES
# U13 boundaries
E=$ROOT/ev-pre; run $E 24576-N STUB_BIN=$S/work TEST_PRECREATE=project; echo "U13 existing project calls=$(cat $E/24576-N/calls)" >> $RES
env DRY=1 TEST_PROJECTS=/tmp/r67-fp OPROOT=$ROOT/op-ev EVIDENCE_DIR=$EV STUB_BIN=$S/work sh $R/operator/run-arm.sh 24576-R > /dev/null 2>&1; echo "U13 duplicate rc=$?" >> $RES
env TEST_TIMEOUT=x sh $R/operator/run-arm.sh 24576-N >/dev/null 2>&1; echo "U13 live seam rc=$?" >> $RES
env DRY=1 STUB_BIN=/var/home/bmosher/.local/bin sh $R/operator/run-arm.sh 24576-N >/dev/null 2>&1; echo "U13 real-claude stub rc=$?" >> $RES
echo "U13 native roots untouched: $(ls -d /tmp/campaign4-r66-op $R/evidence $R/finalized 2>/dev/null | wc -l)" >> $RES
# V1 all 8 labels with approve receipts (fresh finalized dir)
for L in 24576-N 12288-R 24576-I 12288-N 24576-R 12288-I D-12288 D-24576; do rec $EV $L $ROOT/v1-$L.json ok; echo "V1 $L approve: $(fin $EV $L $ROOT/v1-$L.json $ROOT/fin-v1)" >> $RES; done
# V2 content edits in an op-dir copy BEFORE freeze (pins consistent), approve receipt
OPR=$(python -c "import json;[print(json.loads(l)['op']) for l in open('$ROOT/op-ev/map.jsonl') if json.loads(l)['label']=='12288-R']")
v2() { n=$1; py=$2; C=$ROOT/v2op-$n; cp -a $OPR $C; (cd $C && python -c "$py"); E=$ROOT/v2ev-$n; sh $FZ 12288-R $C $E >/dev/null 2>&1; rec $E 12288-R $ROOT/v2r-$n.json ok 2>/dev/null; echo "V2 $n: $(fin $E 12288-R $ROOT/v2r-$n.json $ROOT/v2fin-$n)" >> $RES; }
v2 project_wrong "import json;p=json.load(open('paths.json'));p['project']='/tmp/r67-fp/-tmp-c4x-000000000000';p['project_real']=p['project'];json.dump(p,open('paths.json','w'))"
v2 cwd_not_c4x "import json;p=json.load(open('paths.json'));p['cwd']='/tmp/other';json.dump(p,open('paths.json','w'))"
v2 paths_not_json "open('paths.json','w').write('{broken')"
v2 sid_missing "import re;t=open('arm.s1.meta').read();open('arm.s1.meta','w').write(re.sub(r'^session_id=.*\n','',t,flags=re.M))"
v2 sid_not_uuid "import re;t=open('arm.s2.meta').read();open('arm.s2.meta','w').write(re.sub(r'^session_id=.*$','session_id=not-a-uuid',t,flags=re.M))"
v2 sid_duplicate "import re;a=open('arm.s1.meta').read();s=re.search(r'^session_id=(.*)$',a,re.M).group(1);t=open('arm.s2.meta').read();o=re.search(r'^session_id=(.*)$',t,re.M).group(1);open('arm.s2.meta','w').write(t.replace(o,s))"
v2 meta_sessions_mismatch "import json;m=json.load(open('operator-meta.json'));m['sessions']['s2']='00000000-0000-4000-8000-000000000000';json.dump(m,open('operator-meta.json','w'))"
v2 manifest_malformed "open('mem-after-s1.manifest','w').write('garbage line\n')"
v2 manifest_vs_snapshot "import glob;f=sorted(glob.glob('mem-after-s1/*'))[0];open(f,'a').write('x')"
v2 same_flag_diff_manifests "import glob,hashlib,os;f=sorted(glob.glob('mem-before-s2/*'))[0];open(f,'a').write('x');lines=[];[lines.append(hashlib.sha256(open(p,'rb').read()).hexdigest()+'  ./'+os.path.relpath(p,'mem-before-s2')) for p in sorted(glob.glob('mem-before-s2/*'))];open('mem-before-s2.manifest','w').write('\n'.join(lines)+'\n')"
cat $RES
