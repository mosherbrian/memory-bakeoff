#!/bin/bash
# P13-live-4 supervised operator wrapper. No driver edits.
EV=/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership/live-p13l4
date -u +%Y-%m-%dT%H:%M:%SZ > "$EV/host-start.txt"
env -u EV_DIR -u INJECT_SD -u P13_IN_SCOPE AGENTDECK_PROFILE=campaign4 DRY=0 INJECT=0 \
  /bin/bash /var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership/plans/live-p13-driver.sh \
  /var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership/live-inputs-4.env \
  > "$EV/driver-stdout.txt" 2> "$EV/driver-stderr.txt"
RC=$?
echo "$RC" > "$EV/driver-rc.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$EV/host-end.txt"
cp /home/bmosher/p13-prep-p13l4/passive-director.jsonl "$EV/D_RECORD.jsonl" 2>/dev/null
cp /home/bmosher/p13-prep-p13l4/passive-duty.jsonl "$EV/U_RECORD.jsonl" 2>/dev/null
printf '{"action":"P13-live-4","driver_rc":%s,"host_end_file":"host-end.txt","receiver_records_copied":true}\n' "$RC" > "$EV/end-receipt.json"
AGENTDECK_PROFILE=campaign4 /home/bmosher/.config/agent-deck/wake 0c933c75-1790000758 "P13 live4 complete evidence=/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership/live-p13l4/"
