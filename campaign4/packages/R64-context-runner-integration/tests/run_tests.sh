#!/bin/sh
# R64 offline suite: actual copied runner + finalizer with stubs; fresh ROOT per run. No real claude.
R=$(cd "$(dirname "$0")/.." && pwd); ROOT=${1:?root}; mkdir -p $ROOT; S=$R/tests/stubs; RES=$ROOT/results.txt; : > $RES
run() { lab=$1; shift; env DRY=1 TEST_PROJECTS=/tmp/r64-fp OPROOT=$ROOT/op EVIDENCE_DIR=$ROOT/ev "$@" sh $R/operator/run-arm.sh $lab > $ROOT/out-$lab-$(date +%s%N) 2>&1; echo $?; }
fin() { python $R/operator/finalize.py "$1" "$2" ${3:-$ROOT/ev} $ROOT/fin-$4 | python -c "import json,sys;d=json.load(sys.stdin);print(d.get('status'),d.get('final_primary'),d.get('final_outcome'),d.get('candidate'),'|',d.get('reason','')[:70])"; }
rec() { python - "$@" <<'PY'
import json,hashlib,sys
ev,lab,out,kind=sys.argv[1:5]; a=f"{ev}/{lab}"; h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest(); c=json.load(open(a+"/candidate-r63.json"))["candidate"]
r={"TEST_ONLY":"offline stub receipt, not an independent review","schema":"r63-adjudication-v1","label":lab,"arm_claim_sha256":h(a+"/arm-claim.json"),"reviewer":"corvid-TESTSTUB",
 "log_sha256":c["log_sha256"],"report_sha256":c["report_sha256"],"candidate_outcome":c["outcome"],"decision":"reject" if kind=="reject" else "approve","guessing":False,"contradiction":False,
 "reason":"test","source_evidence":"indeterminate" if kind=="srcind" else "inferred","ask_relevant":"no" if kind=="irrelevant" else ("yes" if c["outcome"]=="asked_no_run" else "not_applicable")}
if kind=="wronglabel": r["label"]="12288-R"
if kind=="wrongclaim": r["arm_claim_sha256"]="0"*64
json.dump(r,open(out,"w"),indent=1)
PY
}
# T1 all 8 labels
for L in 24576-N 12288-R 24576-I 12288-N 24576-R 12288-I D-12288 D-24576; do rc=$(run $L STUB_BIN=$S/work); A=$ROOT/ev/$L
  echo "T1 $L rc=$rc calls=$(cat $A/calls) cand=$(python -c "import json;print(json.load(open('$A/candidate-r63.json'))['candidate']['outcome'])") mem_after_s1=$(head -c 12 $A/mem-after-s1.manifest 2>/dev/null || echo -) hold=[$(tr '\n' ';' < $A/disposition.txt)]" >> $RES; done
H0=$(cd $ROOT/ev && find . -type f | sort | xargs sha256sum | sha256sum)
# T2/T3 finalization on clean arms
rec $ROOT/ev 24576-R $ROOT/r-ok.json ok; echo "T2 approve R: $(fin 24576-R $ROOT/r-ok.json '' a)" >> $RES
echo "T3 no receipt: $(fin 24576-R - '' b)" >> $RES
rec $ROOT/ev 12288-R $ROOT/r-rej.json reject; echo "T3 reject: $(fin 12288-R $ROOT/r-rej.json '' c)" >> $RES
rec $ROOT/ev D-24576 $ROOT/r-si.json srcind; echo "T3 source indeterminate: $(fin D-24576 $ROOT/r-si.json '' d)" >> $RES
rec $ROOT/ev 24576-N $ROOT/r-ir.json irrelevant; echo "T3 irrelevant ask: $(fin 24576-N $ROOT/r-ir.json '' e)" >> $RES
rec $ROOT/ev 12288-N $ROOT/r-nok.json ok; echo "T3 relevant ask approved: $(fin 12288-N $ROOT/r-nok.json '' f)" >> $RES
# T4 binding
rec $ROOT/ev 24576-R $ROOT/r-wl.json wronglabel; echo "T4 receipt wrong label: $(fin 24576-R $ROOT/r-wl.json '' g)" >> $RES
rec $ROOT/ev 24576-R $ROOT/r-wc.json wrongclaim; echo "T4 receipt wrong claim hash: $(fin 24576-R $ROOT/r-wc.json '' h)" >> $RES
echo "T4 receipt for other arm: $(fin 12288-R $ROOT/r-ok.json '' i)" >> $RES
H1=$(cd $ROOT/ev && find . -type f | sort | xargs sha256sum | sha256sum); [ "$H0" = "$H1" ] && echo "T2 bundles unchanged after finalization: yes" >> $RES || echo "T2 bundles unchanged: NO" >> $RES
# T5 tamper copies
for f in log report.md arm.s2.jsonl mem-after-s1.manifest candidate-r63.json operator-meta.json; do T=$ROOT/tamper-$(echo $f | tr ./ __); mkdir -p $T; cp -a $ROOT/ev/24576-R $T/; printf 'x' >> $T/24576-R/$f
  echo "T5 tampered $f: $(fin 24576-R $ROOT/r-ok.json $T j$f)" >> $RES; done
# T6 infrastructure failures, finalized with approve receipts
for c in "s1fail 24576-R STUB_BIN=$S/s1fail" "s2fail 12288-R STUB_BIN=$S/s2fail" "gate1 24576-I STUB_BIN=$S/work GATE=$S/gate1.py" "evfail 12288-I STUB_BIN=$S/work EVENTS=$S/ev_fail.py" "mutate 24576-R STUB_BIN=$S/work TEST_MUTATE_BETWEEN=1"; do
  set -- $c; n=$1; L=$2; shift 2; E=$ROOT/ev-$n; env DRY=1 TEST_PROJECTS=/tmp/r64-fp OPROOT=$ROOT/op-$n EVIDENCE_DIR=$E "$@" sh $R/operator/run-arm.sh $L > $ROOT/out-$n 2>&1
  rec $E $L $ROOT/r-$n.json ok 2>/dev/null; echo "T6 $n calls=$(cat $E/$L/calls) hold=[$(tr '\n' ';' < $E/$L/disposition.txt)] -> $(fin $L $ROOT/r-$n.json $E k$n)" >> $RES; done
# T7 boundaries
E=$ROOT/ev-pre; env DRY=1 TEST_PROJECTS=/tmp/r64-fp OPROOT=$ROOT/op-pre EVIDENCE_DIR=$E STUB_BIN=$S/work TEST_PRECREATE=project sh $R/operator/run-arm.sh 24576-N > $ROOT/out-pre 2>&1; echo "T7 existing project rc=$? calls=$(cat $E/24576-N/calls)" >> $RES
n0=$(ls -d $ROOT/op/o-* | wc -l); env DRY=1 TEST_PROJECTS=/tmp/r64-fp OPROOT=$ROOT/op EVIDENCE_DIR=$ROOT/ev STUB_BIN=$S/work sh $R/operator/run-arm.sh 24576-R > $ROOT/out-dup 2>&1; echo "T7 duplicate rc=$? new_opdirs=$(( $(ls -d $ROOT/op/o-* | wc -l) - n0 ))" >> $RES
env TEST_TIMEOUT=x sh $R/operator/run-arm.sh 24576-N > $ROOT/out-seam 2>&1; echo "T7 live seam rc=$? $(head -1 $ROOT/out-seam)" >> $RES
env DRY=1 STUB_BIN=/var/home/bmosher/.local/bin sh $R/operator/run-arm.sh 24576-N > $ROOT/out-real 2>&1; echo "T7 real-claude stub rc=$? $(head -1 $ROOT/out-real)" >> $RES
echo "T7 refinalize no overwrite: $(python $R/operator/finalize.py 24576-R $ROOT/r-ok.json $ROOT/ev $ROOT/fin-a >/dev/null 2>&1; echo rc=$?)" >> $RES
cat $RES
