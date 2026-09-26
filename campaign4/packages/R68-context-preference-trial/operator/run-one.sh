#!/bin/sh
# R68 one arm: preflight (must pass) -> commit -> run unchanged R67 runner with all seams unset -> byte-identical archive -> summary.
L=$1; P=/var/home/bmosher/memory-bake-off/campaign4/packages; Q=$P/R68-context-preference-trial; A=$P/R67-identity-boundary-validation/evidence/$L
U="-u STUB_BIN -u DRY -u TEST_PROJECTS -u TEST_PRECREATE -u TEST_MUTATE_BETWEEN -u TEST_TIMEOUT -u GATE -u EVENTS -u OPROOT -u EVIDENCE_DIR -u R67_TEST_PROJECTS"
cd $Q && env $U python operator/preflight.py $L > /dev/null || { echo "PREFLIGHT FAILED"; cat operator/preflight-$L.json; exit 1; }
git add operator/preflight-$L.json && git commit -qm "R68: preflight $L before calls"
cd /var/home/bmosher && env $U sh $P/R67-identity-boundary-validation/operator/run-arm.sh $L > $Q/operator/run-$L.out 2>&1; echo rc=$? >> $Q/operator/run-$L.out
cp -a $A $Q/evidence/$L && diff -r $A $Q/evidence/$L > /dev/null && echo BYTE_IDENTICAL || echo ARCHIVE_DIFF
cat $Q/operator/run-$L.out; echo "calls=$(cat $A/calls) disp=[$(tr '\n' ';' < $A/disposition.txt)] mem_compare=$(cat $A/mem-compare 2>/dev/null || echo -)"
for n in 1 2; do [ -f $A/arm.s$n.meta ] && echo "s$n $(grep -E '^(exit|wrapper_rc)' $A/arm.s$n.meta | tr '\n' ' ') scan=$(python -c "import json;d=json.load(open('$A/scan-gate-s$n.json'));print(d.get('rc'),d.get('gate'))" 2>&1) events=$(python -c "import json;print(json.load(open('$A/events-s$n.json'))['counts'])" 2>&1)"; done
for f in before-s1 after-s1 before-s2 after-s2; do [ -f $A/mem-$f.manifest ] && echo "$f: $(tr '\n' ' ' < $A/mem-$f.manifest | cut -c1-160)"; done
cat $A/report.md; echo; cat $A/log; python -c "import json;d=json.load(open('$A/candidate-r63.json'));print('candidate',d['candidate']['outcome'],'|',d['candidate']['reason'],'| gate',d['gate']['status'])"
python -c "
import json
for n in (1,2):
  try: f=open('$A/arm.s%d.jsonl'%n)
  except OSError: continue
  for l in f:
    d=json.loads(l)
    if d.get('type')=='assistant':
      for c in d['message']['content']:
        if c.get('type')!='thinking': print('s%d'%n,c.get('type'),str(c.get('text') or c.get('input'))[:170])"
echo "arm_claim=$(sha256sum $A/arm-claim.json|cut -c1-64) log=$(sha256sum $A/log|cut -c1-64) report=$(sha256sum $A/report.md|cut -c1-64)"
