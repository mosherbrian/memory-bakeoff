#!/bin/sh
# R59 actual-runner tests with local stubs only (no real claude, fake projects root /tmp/r59-fp). Output: tests/results.txt
S=/home/bmosher/memory-bake-off/campaign4/packages/R59-context-readiness-completion/tests/stubs; R=/home/bmosher/memory-bake-off/campaign4/packages/R59-context-readiness-completion; : > $R/tests/results.txt; rm -f /tmp/r59-s2c-* 2>/dev/null
t() { name=$1; label=$2; shift 2; ev=/tmp/r59-ev-$name; env DRY=1 OPROOT=/tmp/r59-op-$name EVIDENCE_DIR=$ev TEST_PROJECTS=/tmp/r59-fp "$@" sh $R/operator/run-arm.sh $label > /tmp/r59-out-$name 2>&1; rc=$?
  B=$ev/$label; echo "$name rc=$rc calls=$(cat $B/calls 2>/dev/null || echo -) hold=[$(tr '\n' ';' < $B/disposition.txt 2>/dev/null)] mem=$(cat $B/mem-after-s1.manifest 2>/dev/null | head -1 | cut -c1-20)/$(cat $B/mem-compare 2>/dev/null) events=$(ls $B/events-s*.json 2>/dev/null | wc -l) grade=$(python -c "import json;print(json.load(open('$B/grade-r57.json'))['outcome'])" 2>/dev/null || echo -) bundle=$([ -f $B/arm-claim.json ] && echo yes || echo no) sim=$([ -d $B/arm-final ] && echo yes || echo no)" >> $R/tests/results.txt; }
t clean_R 24576-R STUB_BIN=$S/save
t clean_N 12288-N STUB_BIN=$S/ok
t clean_D D-24576 STUB_BIN=$S/ok
t empty_dir 24576-I STUB_BIN=$S/emptydir
t boundary_change 24576-N STUB_BIN=$S/ok TEST_MUTATE_BETWEEN=1
t parent_only 24576-N STUB_BIN=$S/ok TEST_PRECREATE=project
t memory_exists 24576-N STUB_BIN=$S/ok TEST_PRECREATE=memory
t s1_fail 24576-R STUB_BIN=$S/s1fail
t s2_fail 24576-N STUB_BIN=$S/s2fail
t missing_meta 24576-N STUB_BIN=$S/ok TEST_TIMEOUT=$S/to0nometa
t timeout 24576-N STUB_BIN=$S/ok TEST_TIMEOUT=$S/to124
t kill 24576-N STUB_BIN=$S/ok TEST_TIMEOUT=$S/to137
t D_fail D-12288 STUB_BIN=$S/Dfail
for g in 1 2 3 5; do t gate$g 24576-N STUB_BIN=$S/ok GATE=$S/gate$g.py; done
t events_flag 24576-N STUB_BIN=$S/ok EVENTS=$S/ev_flag.py
t events_fail 24576-N STUB_BIN=$S/ok EVENTS=$S/ev_fail.py
# duplicate: second run of an existing label must stop before any call
env DRY=1 OPROOT=/tmp/r59-op-dup EVIDENCE_DIR=/tmp/r59-ev-clean_R TEST_PROJECTS=/tmp/r59-fp STUB_BIN=$S/save sh $R/operator/run-arm.sh 24576-R > /tmp/r59-out-dup 2>&1; echo "duplicate rc=$? opdirs_created=$(ls -d /tmp/r59-op-dup/o-* 2>/dev/null | wc -l) msg=$(head -1 /tmp/r59-out-dup)" >> $R/tests/results.txt
# seam guard: seam variable without STUB_BIN refused before any call; STUB_BIN pointing at real claude refused
env TEST_TIMEOUT=$S/to124 sh $R/operator/run-arm.sh 24576-N > /tmp/r59-out-g1 2>&1; echo "seam_live_refused rc=$? msg=$(head -1 /tmp/r59-out-g1)" >> $R/tests/results.txt
env DRY=1 STUB_BIN=/var/home/bmosher/.local/bin sh $R/operator/run-arm.sh 24576-N > /tmp/r59-out-g2 2>&1; echo "seam_realclaude_refused rc=$? msg=$(head -1 /tmp/r59-out-g2)" >> $R/tests/results.txt
# bundle integrity: every arm-claim hash recomputes; no temp dirs left
python - <<'PY' >> $R/tests/results.txt
import json, hashlib, glob, os
bad=[]; n=0
for c in glob.glob("/tmp/r59-ev-*/*/arm-claim.json"):
    d=os.path.dirname(c); j=json.load(open(c)); n+=1
    for f,v in j["files_sha256"].items():
        if hashlib.sha256(open(os.path.join(d,f),"rb").read()).hexdigest()!=v: bad.append((c,f))
tmp=glob.glob("/tmp/r59-ev-*/.tmp-*")
print(f"bundle_integrity bundles={n} hash_mismatches={len(bad)} temp_leftovers={len(tmp)}")
PY
