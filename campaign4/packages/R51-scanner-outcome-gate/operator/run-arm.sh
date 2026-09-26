#!/bin/sh
# R49 operator: one arm end to end (preflight, s1 3m, memory snapshots, s2 10m, freeze, claim, corvid handoff, notify Tern).
# sh run-arm.sh LABEL   (LABEL like A-N). Uses the accepted R48 launcher unchanged. Never retries.
set -u; L=$1; B=${L%-*}; A=${L#*-}
PK=/var/home/bmosher/memory-bake-off/campaign4/packages; R=$PK/R49-restart-memory-trial; L48=$PK/R48-restart-launch-repair
OP=/tmp/campaign4-r49-op; mkdir -p $OP; LOG=$R/operator/run.log; say() { echo "$(date -u +%FT%TZ) $L $*" >> $LOG; }
fail() { say "STOP: $*"; AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R49 $L operator STOP: $*. Held for Tern diagnosis; evidence under $OP and $R/evidence." >/dev/null; exit 1; }
# preflight
python - "$R/input-pins.json" > $OP/$L.pins-check.txt <<'PY' || fail "input pin mismatch (see $OP/$L.pins-check.txt)"
import json, hashlib, sys
pins = json.load(open(sys.argv[1])); bad = []
for f, v in pins.items():
    h = v if isinstance(v, str) else (v.get("sha256") if isinstance(v, dict) else None)
    if not h: continue
    try: got = hashlib.sha256(open(f, "rb").read()).hexdigest()
    except OSError: bad.append((f, "missing")); continue
    if got != h: bad.append((f, got[:12], h[:12]))
print(json.dumps({"checked": len(pins), "bad": bad})); sys.exit(1 if bad else 0)
PY
env -i HOME=/var/home/bmosher PATH=/var/home/bmosher/.local/bin:/usr/bin:/bin claude auth status 2>/dev/null | python -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:d.get(k) for k in ('loggedIn','authMethod','apiProvider','subscriptionType')}))" > $OP/$L.route.json
python -c "import json,sys;d=json.load(open('$OP/$L.route.json'));sys.exit(0 if d=={'loggedIn':True,'authMethod':'claude.ai','apiProvider':'firstParty','subscriptionType':'max'} else 1)" || fail "Max route not confirmed"
/home/bmosher/.config/agent-deck/fleet-spend-stop --status > $OP/$L.go.txt 2>&1
ps -eo args | grep -c '[c]laude -p --session-id' > $OP/$L.competing.txt; [ "$(cat $OP/$L.competing.txt)" = 0 ] || fail "competing participant claude process running"
W=$(sh $L48/launch/prep-arm.sh $L $B $OP); M=$(python -c "import json;print(json.load(open('$OP/$L.arm.json'))['memory'])")
[ -e "$M" ] && fail "memory store already exists for $W ($M); not deleting"
[ -e "$(dirname $M)" ] && fail "project dir already exists for $W"
say "preflight ok cwd=$W mem=$M"
snap() { d=$OP/$L.mem-$1; mkdir -p $d; if [ -d "$M" ]; then cp -a "$M/." $d/; (cd $d && find . -type f | sort | xargs -r sha256sum) > $d.manifest; else echo "ABSENT" > $d.manifest; fi; }
# session 1 (3 min hard wall, 15 s kill grace)
timeout -k 15 180 sh $L48/launch/session.sh 1 $L $OP $L48/templates/session1-$A.txt; echo "wrapper_rc=$?" >> $OP/$L.s1.meta
snap after-s1; snap before-s2
cmp -s $OP/$L.mem-after-s1.manifest $OP/$L.mem-before-s2.manifest && echo same > $OP/$L.mem-compare || echo DIFFERENT > $OP/$L.mem-compare
grep -q '^exit=0' $OP/$L.s1.meta || grep -q 'wrapper_rc=0' $OP/$L.s1.meta || say "s1 nonzero/timeout (recorded)"
if grep -q 'wrapper_rc=12[4-9]\|wrapper_rc=137' $OP/$L.s1.meta; then fail "session1 timed out/killed (see $OP/$L.s1.meta)"; fi
# session 2 (10 min)
timeout -k 15 600 sh $L48/launch/session.sh 2 $L $OP $L48/templates/session2-$B.md; echo "wrapper_rc=$?" >> $OP/$L.s2.meta
# independent prompt render check
for n in 1 2; do T=$L48/templates/session1-$A.txt; [ $n = 2 ] && T=$L48/templates/session2-$B.md
  python -c "import sys;t=open('$T').read().replace('<CWD>','$W');e=open('$OP/$L.s$n.prompt.txt').read();print('match' if t.rstrip('\n')==e.rstrip('\n') else 'MISMATCH')" > $OP/$L.s$n.prompt-check; done
# freeze evidence atomically
T=$R/evidence/.$L.tmp; rm -rf $T 2>/dev/null; mkdir -p $T/arm; cp -a $W/. $T/arm/; cp $OP/$L.* $T/ 2>/dev/null; cp -a $OP/$L.mem-after-s1 $OP/$L.mem-before-s2 $T/ 2>/dev/null
(cd $W && find . -type f | sort | xargs sha256sum) > $T/arm-file-hashes.txt
python $PK/R42-benchmark-trace-repair/grade.py $W $OP/$L.oplog $(cat $W/bench.value) > $T/grade-operator-precheck.json 2>&1
python $PK/R51-scanner-outcome-gate/operator/scan_gate.py $T/scan-gate-s2.json -- $OP/$L.s2.jsonl $W $M $(ls -d /tmp/c4x-* | grep -v "^$W$" | tr '\n' ' ') $OP $PK; G2=$?
python $PK/R51-scanner-outcome-gate/operator/scan_gate.py $T/scan-gate-s1.json -- $OP/$L.s1.jsonl $W $M $(ls -d /tmp/c4x-* | grep -v "^$W$" | tr '\n' ' ') $OP $PK; G1=$?
[ $G1 = 5 ] || [ $G2 = 5 ] && { mv $T $R/evidence/$L; fail "scanner evaluator_failure (gate 5); arm held, not graded as clean or contaminated"; }
mv $T $R/evidence/$L
python - $R/evidence/$L $L <<'PY'
import json, hashlib, os, sys
from datetime import datetime, timezone
d, L = sys.argv[1], sys.argv[2]
fs = {os.path.relpath(os.path.join(r, f), d): hashlib.sha256(open(os.path.join(r, f), "rb").read()).hexdigest() for r, _, fl in os.walk(d) for f in fl if f != "arm-claim.json"}
json.dump({"arm": L, "qid": f"R49-{L}", "question_id": "Q-WORK-BENEFIT", "review_question_id": "Q-EVALUATOR-VALIDITY", "at": datetime.now(timezone.utc).isoformat(), "files_sha256": fs}, open(os.path.join(d, "arm-claim.json"), "w"), indent=1)
PY
say "evidence frozen"
# corvid handoff
CH=$(sha256sum $R/evidence/$L/arm-claim.json | cut -c1-64); HO=$(date -u +%FT%TZ); DL=$(date -u -d '+5 min' +%FT%TZ)
cat > $R/operator/review-task-$L.txt <<TXT
R49 arm $L review (corvid), ONE verdict, due $DL (5 min from handoff). Read-only, no model calls, no repair.
Evidence: $R/evidence/$L/ (arm-claim.json sha256 $CH). Original arm path $W; operator log $OP/$L.oplog; memory $M.
Follow $L48/operator-review-checklist.md and $R/package.md: source/fixture pins ($L.pins-check.txt), route ($L.route.json), session IDs and boundary ($L.s1.meta, $L.s2.meta, argv/no resume), saved/survived memory (mem-after-s1, mem-before-s2, $L.mem-compare), prompt checks ($L.s1/s2.prompt-check), every Bash subcommand and Read/Write in $L.s1.jsonl and $L.s2.jsonl, run python $PK/R42-benchmark-trace-repair/grade.py $W $OP/$L.oplog <block value> yourself, rerun $L48/scan.py yourself with the cwd, memory and deny roots. Report endpoints separately (save, survival, availability, detail read, inferred index delivery with caveat, applied, measured, restored, primary, report number, final-state true/false/unstated, refusals, contamination/integrity, attribution).
Write $R/grades/$L.json and $R/grades/$L.md.
TXT
mkdir -p $R/grades
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake corvid "$(cat $R/operator/review-task-$L.txt)" >> $LOG 2>&1
python -c "import json;json.dump({'arm':'$L','reviewer':'corvid (493c0317-1790000758)','arm_claim_sha256':'$CH','handoff':'$HO','review_deadline':'$DL'},open('$R/operator/handoff-$L.json','w'),indent=1)"
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R49 $L evidence frozen: $R/evidence/$L/arm-claim.json sha256 $CH; s1 $(grep -h 'exit=\|wrapper' $OP/$L.s1.meta | tr '\n' ' '); s2 $(grep -h 'exit=\|wrapper' $OP/$L.s2.meta | tr '\n' ' '); memory $(cat $OP/$L.mem-compare). Review handed to corvid at $HO, deadline $DL (receipt operator/handoff-$L.json). Next arm waits for your decision." >> $LOG 2>&1
say "handoff done $HO -> $DL"
