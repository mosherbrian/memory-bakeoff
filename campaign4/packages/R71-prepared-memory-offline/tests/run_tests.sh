#!/bin/sh
# R71 offline suite: actual copied runner + finalizer, stub modes; fresh ROOT; native roots untouched.
R=$(cd "$(dirname "$0")/.." && pwd); ROOT=${1:?root}; mkdir -p $ROOT; S=$R/tests/stubs/r71; RES=$ROOT/results.txt; : > $RES; export R67_TEST_PROJECTS=/tmp/r71-fp
FN=$R/operator/finalize.py; i=0
run() { L=$1; mode=$2; echo $mode > $S/mode; echo ${L%%-*} > $S/target; E=$ROOT/ev$i; env DRY=1 TEST_PROJECTS=/tmp/r71-fp OPROOT=$ROOT/op$i EVIDENCE_DIR=$E STUB_BIN=$S sh $R/operator/run-arm.sh $L > $ROOT/out$i 2>&1; echo $E; }
rec() { python - "$@" <<'PY'
import json,hashlib,sys
E,L,out,kind=sys.argv[1:5]; a=f"{E}/{L}"; h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest(); c=json.load(open(a+"/candidate-r63.json"))["candidate"]
json.dump({"TEST_ONLY":"stub receipt","schema":"r63-adjudication-v1","label":L,"arm_claim_sha256":h(a+"/arm-claim.json"),"reviewer":"corvid-TESTSTUB","log_sha256":c["log_sha256"],"report_sha256":c["report_sha256"],
 "candidate_outcome":c["outcome"],"decision":"approve","guessing":c["outcome"]=="target_guessed","contradiction":False,"reason":"test","source_evidence":"observed","ask_relevant":"yes" if c["outcome"]=="asked_no_run" else "not_applicable"},open(out,"w"))
PY
}
evrec() { python - "$@" <<'PY'
import json,hashlib,sys
E,L,out,mut=sys.argv[1:5]; a=f"{E}/{L}"; h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
CJ=lambda o: hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
ev=json.load(open(a+"/events-s2.json")); uses={};res={}
for l in open(a+"/arm.s2.jsonl"):
    e=json.loads(l); m=e.get("message") or {}
    for c in (m.get("content") or []):
        if c.get("type")=="tool_use": uses[c["id"]]=c
        if c.get("type")=="tool_result": res[c["tool_use_id"]]=c
items=[{"tool_use_id":x["id"],"category":"C2","tool_use_sha256":CJ(uses[x["id"]]["input"]),"tool_result_sha256":CJ(res[x["id"]]["content"]),"reason":"test"} for x in ev["memory_events"] if x["event"]=="unsupported_shell"]
r={"TEST_ONLY":"stub","schema":"r69-event-adjudication-v1","label":L,"arm_claim_sha256":h(a+"/arm-claim.json"),"transcript_sha256":h(a+"/arm.s2.jsonl"),"events_sha256":h(a+"/events-s2.json"),"reviewer":"corvid-TESTSTUB","events":items}
if mut=="stale": r["transcript_sha256"]="0"*64
if mut=="wrongarm": r["label"]="12288-RD"
if mut=="missing": r["events"]=[]
json.dump(r,open(out,"w"))
PY
}
fin() { E=$1; L=$2; SR=$3; ER=$4; python $FN $L $SR $E $E-fin $ER > $ROOT/fin.json 2>&1; rc=$?; python -c "import json;d=json.load(open('$ROOT/fin.json'));print('rc=$rc',d['status'],d['final_primary'],d.get('final_outcome'),'A4='+str((d.get('axes') or {}).get('A4_observed_detail_read')),'|',d['reason'][:70])" 2>&1 | head -1; }
cand() { python -c "import json;print(json.load(open('$1/$2/candidate-r63.json'))['candidate']['outcome'])" 2>/dev/null || echo NONE; }
X() { tag=$1; L=$2; mode=$3; i=$((i+1)); E=$(run $L $mode); rec $E $L $ROOT/sr$i.json k; echo "$tag $L $mode calls=$(cat $E/$L/calls 2>/dev/null) cand=$(cand $E $L) disp=[$(tr '\n' ';' < $E/$L/disposition.txt 2>/dev/null)] -> $(fin $E $L $ROOT/sr$i.json)" >> $RES; LAST=$E; }
X X1 24576-RD rdread; X X1 12288-ID ask; X X1 12288-N ask; X X1 12288-RD rdread; X X1 24576-ID ask; X X1 24576-N ask
X X2 12288-RD rdnoread
X X3 12288-ID guessok; X X4 24576-ID guesswrong
X X5 24576-RD rduser; X X6 12288-ID idmemory
X X8a 24576-N ncompound; E=$LAST; evrec $E 24576-N $ROOT/er-ok.json ok; echo "X8b 24576-N with C2 receipt -> $(fin $E 24576-N $ROOT/sr$i.json $ROOT/er-ok.json)" >> $RES
for m in stale wrongarm missing; do evrec $E 24576-N $ROOT/er-$m.json $m; echo "X10 event receipt $m -> $(fin $E 24576-N $ROOT/sr$i.json $ROOT/er-$m.json)" >> $RES; done
X X9a 12288-RD rdcompound; E=$LAST; evrec $E 12288-RD $ROOT/er9.json ok; echo "X9b 12288-RD compound with C2 receipt -> $(fin $E 12288-RD $ROOT/sr$i.json $ROOT/er9.json)" >> $RES
X X10r 12288-N redirect; E=$LAST; evrec $E 12288-N $ROOT/er10.json ok; echo "X10 redirect with receipt -> $(fin $E 12288-N $ROOT/sr$i.json $ROOT/er10.json)" >> $RES
# X7 leak: bad fixture copy in a temp R71 clone is out of scope; instead corrupt via runner seam-free check on a temp fixture dir
cp -a $R/fixtures $ROOT/fixtures-backup; printf -- '- [x](y.md) 24576 note\n' > $ROOT/leakidx; cp $R/fixtures/ID/MEMORY.md $ROOT/idx.orig; cp $ROOT/leakidx $R/fixtures/ID/MEMORY.md
i=$((i+1)); E=$(run 24576-ID ask); cp $ROOT/idx.orig $R/fixtures/ID/MEMORY.md; echo "X7 leaked ID index calls=$(cat $E/24576-ID/calls) disp=[$(tr '\n' ';' < $E/24576-ID/disposition.txt)]" >> $RES
# X11 fixture tampered between seed and session: covered by finalizer compare -> edit a copy's claim is post-freeze; use leak run bundle (fixture differs) as evidence
echo "X11 leak-run bundle finalize -> $(fin $E 24576-ID -)" >> $RES
i=$((i+1)); E=$(run 24576-RD rdread); echo "X12 no receipt -> $(fin $E 24576-RD -)" >> $RES; rec $E 24576-RD $ROOT/x12.json k; echo "X12 then valid -> $(fin $E 24576-RD $ROOT/x12.json)" >> $RES; echo "X12 refinalize -> $(fin $E 24576-RD $ROOT/x12.json)" >> $RES
env DRY=1 TEST_PROJECTS=/tmp/r71-fp OPROOT=$ROOT/op1 EVIDENCE_DIR=$ROOT/ev1 STUB_BIN=$S sh $R/operator/run-arm.sh 24576-RD > /dev/null 2>&1; echo "X12 duplicate rc=$?" >> $RES
env -u STUB_BIN -u R71_LIVE_RELEASE sh $R/operator/run-arm.sh 24576-RD > $ROOT/live.out 2>&1; echo "X12 live refused rc=$? $(head -1 $ROOT/live.out)" >> $RES
env TEST_TIMEOUT=x R71_LIVE_RELEASE=x sh $R/operator/run-arm.sh 24576-RD > $ROOT/seam.out 2>&1; echo "X12 live seam refused rc=$? $(head -1 $ROOT/seam.out)" >> $RES
cat $RES
