#!/bin/sh
# R43 driver (R39 process): per arm in frozen order: dispatch (arm.py: idle check, /new, dispatch, root binding),
# wait for the worker step to end, snapshot the ORIGINAL arm into evidence/<arm>/ before grading, wait for the
# verifier, wake Tern with the exact decide command, wait for Tern's decision. Stops on anything unexpected.
R=/home/bmosher/memory-bake-off/campaign4/packages/R43-service-restoration-trial; cd $R/operator
AL=/home/bmosher/.local/bin/agent-loop; CFG=/home/bmosher/.config/agent-loop/campaign4.json
step() { $AL status --config $CFG --json | python -c "import json,sys;print(next((p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'),'none'))"; }
for a in A-N A-I A-R C-R C-N C-I B-I B-R B-N; do
  q=R43-$a; A=/tmp/campaign4-r43/arms/$a; L=/tmp/campaign4-r43/operator/$a.oplog
  python arm.py $a >> drive.log 2>&1 || { echo "$(date -u +%T) STOP: dispatch/preflight failed for $a" >> drive.log; AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R43 operator: preflight/dispatch failed for $a; driver stopped; Claude diagnoses."; exit 1; }
  end=$(( $(date +%s) + 900 )); while [ "$(step $q)" = worker ] && [ $(date +%s) -lt $end ]; do sleep 5; done
  S=$R/evidence/$a; mkdir -p $S; cp -r $A/state $S/state; cp $A.state-before $S/; cp -r $A/out $S/ 2>/dev/null; cp $A/report.md $S/ 2>/dev/null; cp $L $S/operator.oplog
  cp /home/bmosher/memory-bake-off/campaign4/handin/r43/$a-report.md $S/handin-report.md 2>/dev/null
  (cd $A && find . -type f | sort | xargs sha256sum) > $S/arm-file-hashes.txt; echo "$(date -u +%FT%TZ) step=$(step $q)" > $S/snapshot-at.txt
  echo "$(date -u +%T) snapshot $a at step $(step $q)" >> drive.log
  ./wait-arm.sh $q >> drive.log
  s=$(step $q)
  if [ "$s" != decision ]; then echo "$(date -u +%T) STOP: $q step=$s" >> drive.log; AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R43 operator: $q reached step '$s', not a verifier result. Driver stopped; Claude diagnoses before any next arm."; exit 1; fi
  AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "$q verifier filed (stream A outcome + stream B validity check). Grade: $R/grades/$a.json; raw: $R/evidence/$a-grade-raw.json; snapshot: $R/evidence/$a/. Decide: $AL decide --config $CFG --qid $q --kind <KIND> --ref $R/grades/$a.json --reason \"<reason>\". Next arm waits for your decision." >> drive.log 2>&1
  ./wait-decide.sh $q >> drive.log
  [ "$(step $q)" = closed ] || { echo "$(date -u +%T) STOP: $q not closed after 30 min" >> drive.log; exit 1; }
done
echo "$(date -u +%T) ALL NINE ARMS CLOSED" >> drive.log
