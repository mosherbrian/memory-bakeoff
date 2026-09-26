#!/bin/sh
# R68: wait for the complete review (grades json+md + receipt), recheck sources/env/receipt binding, run the R67 finalizer ONCE.
# sh finalize-arm.sh LABEL [WAIT_SECONDS]
L=$1; W=${2:-900}; P=/var/home/bmosher/memory-bake-off/campaign4/packages; Q=$P/R68-context-preference-trial; A=$P/R67-identity-boundary-validation/evidence/$L
i=0; until [ -s $Q/grades/$L.json ] && [ -s $Q/grades/$L.md ] && python -c "import json;json.load(open('$Q/receipts/$L.json'))" 2>/dev/null; do i=$((i+5)); [ $i -ge $W ] && { echo "NO complete review by $(date -u +%T)"; exit 2; }; sleep 5; done
sleep 5
env -u STUB_BIN -u DRY -u TEST_PROJECTS -u TEST_PRECREATE -u TEST_MUTATE_BETWEEN -u TEST_TIMEOUT -u GATE -u EVENTS -u OPROOT -u EVIDENCE_DIR -u R67_TEST_PROJECTS python - "$L" <<'PY' || exit 3
import json,hashlib,os,sys
L=sys.argv[1]; P="/var/home/bmosher/memory-bake-off/campaign4/packages"; Q=P+"/R68-context-preference-trial"; A=P+"/R67-identity-boundary-validation/evidence/"+L
h=lambda p:hashlib.sha256(open(p,"rb").read()).hexdigest(); m=json.load(open(Q+"/operator/source-manifest.json"))
bad=[f for f,v in m["files"].items() if h(os.path.join(P,f))!=v]; assert not bad, ("source changed",bad)
r=json.load(open(f"{Q}/receipts/{L}.json"))
assert r.get("label")==L and r.get("arm_claim_sha256")==h(A+"/arm-claim.json") and r.get("log_sha256")==h(A+"/log") and r.get("report_sha256")==h(A+"/report.md"), "receipt not bound"
assert not os.path.exists(f"{Q}/finalized/{L}/terminal.json"), "terminal exists"
print("prefinal ok")
PY
PRE=$(cd $A && find . -type f | sort | xargs sha256sum | sha256sum)
env -u STUB_BIN -u DRY -u TEST_PROJECTS -u TEST_PRECREATE -u TEST_MUTATE_BETWEEN -u TEST_TIMEOUT -u GATE -u EVENTS -u OPROOT -u EVIDENCE_DIR -u R67_TEST_PROJECTS \
  python $P/R67-identity-boundary-validation/operator/finalize.py $L $Q/receipts/$L.json $P/R67-identity-boundary-validation/evidence $Q/finalized > $Q/operator/finalize-$L.out 2>&1; rc=$?
POST=$(cd $A && find . -type f | sort | xargs sha256sum | sha256sum)
echo "finalize rc=$rc bundle_unchanged=$([ "$PRE" = "$POST" ] && echo yes || echo NO)"; cat $Q/operator/finalize-$L.out
