#!/bin/sh
# R37 driver: for C then T: dispatch (arm.py), wait until the worker step ends, snapshot the arm (outbox, witness,
# origin refs, checkout log) BEFORE grading, wait for the verifier, wake Tern with the exact decide command,
# wait for Tern's decision. Stops on anything unexpected.
R=/home/bmosher/memory-bake-off/campaign4/packages/R37-patch-delivery-pilot; cd $R/operator
AL=/home/bmosher/.local/bin/agent-loop; CFG=/home/bmosher/.config/agent-loop/campaign4.json
step() { $AL status --config $CFG --json | python -c "import json,sys;print(next((p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'),'none'))"; }
for a in C T; do
  q=R37-$a
  python arm.py $a >> drive.log 2>&1 || { echo "$(date -u +%T) STOP: dispatch/preflight failed for $a" >> drive.log; exit 1; }
  end=$(( $(date +%s) + 900 )); while [ "$(step $q)" = worker ] && [ $(date +%s) -lt $end ]; do sleep 5; done
  S=$R/evidence/$a-snapshot; mkdir -p $S; cp -r /var/home/bmosher/r37-arms/$a/outbox $S/ 2>/dev/null; cp /var/home/bmosher/r37-operator/$a.witness $S/witness.log
  git -C /var/home/bmosher/r37-arms/$a/origin.git for-each-ref --format='%(objectname) %(refname)' > $S/origin-refs.txt
  git -C /var/home/bmosher/r37-arms/$a/pi-lcm log --all --oneline --decorate > $S/checkout-log.txt 2>&1; git -C /var/home/bmosher/r37-arms/$a/pi-lcm status --short > $S/checkout-status.txt 2>&1
  echo "$(date -u +%T) snapshot $a at step $(step $q)" >> drive.log
  ./wait-arm.sh $q >> drive.log
  s=$(step $q)
  if [ "$s" != decision ]; then echo "$(date -u +%T) STOP: $q step=$s" >> drive.log; AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R37 operator: $q reached step '$s', not a verifier result. Driver stopped; Claude diagnoses before any next arm."; exit 1; fi
  AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "$q verifier filed. Grade: $R/grades/$a.json. Decide: $AL decide --config $CFG --qid $q --kind <KIND> --ref $R/grades/$a.json --reason \"<reason>\". Next arm (if any) waits for your decision." >> drive.log 2>&1
  ./wait-decide.sh $q >> drive.log
  [ "$(step $q)" = closed ] || { echo "$(date -u +%T) STOP: $q not closed after 30 min" >> drive.log; exit 1; }
done
echo "$(date -u +%T) BOTH ARMS CLOSED" >> drive.log
