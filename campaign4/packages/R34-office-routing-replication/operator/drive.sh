#!/bin/sh
# R34 operator driver: for each arm in frozen order (the first is already dispatched), wait for the grade,
# wake Tern with the exact decide command, wait for Tern's decision (package closed), then dispatch the next.
# Stops (no improvising) on any arm that does not reach the director's decision, or on a preflight failure.
R=/home/bmosher/memory-bake-off/campaign4/packages/R34-office-routing-replication; cd $R/operator
AL=/home/bmosher/.local/bin/agent-loop; CFG=/home/bmosher/.config/agent-loop/campaign4.json
step() { $AL status --config $CFG --json | python -c "import json,sys;print(next((p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'),'none'))"; }
first=1
for pa in S-C S-T V-T V-C L-C L-T; do
  q=R34-$pa
  if [ $first = 0 ]; then python arm.py $pa >> drive.log 2>&1 || { echo "$(date -u +%T) STOP: dispatch/preflight failed for $pa" >> drive.log; exit 1; }; fi
  first=0
  ./wait-arm.sh $q >> drive.log
  s=$(step $q)
  if [ "$s" != decision ]; then echo "$(date -u +%T) STOP: $q step=$s (not a verifier result)" >> drive.log; AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "R34 operator: $q reached step '$s', not a verifier result. Driver stopped; Claude diagnoses before any next arm." ; exit 1; fi
  AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake tern "$q verifier filed. Grade: $R/grades/$pa.json. Decide: $AL decide --config $CFG --qid $q --kind <KIND> --ref $R/grades/$pa.json --reason \"<reason>\". Next frozen arm waits for your decision." >> drive.log 2>&1
  ./wait-decide.sh $q >> drive.log
  [ "$(step $q)" = closed ] || { echo "$(date -u +%T) STOP: $q not closed after 30 min" >> drive.log; exit 1; }
done
echo "$(date -u +%T) ALL SIX ARMS CLOSED" >> drive.log
