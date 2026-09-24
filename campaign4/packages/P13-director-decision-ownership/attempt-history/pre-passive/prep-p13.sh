#!/bin/bash
# P13 PREPARATION ONLY (separate grant). Launches four FRESH idle ACP fixture seats in the campaign4
# profile, the way P12-prepare-1/2 did (agent-deck launch WORKDIR -t NAME -cmd <ACP lane>), after arming an
# explicit-UTC calendar cleanup fallback that removes ONLY the IDs recorded in fixture-ids.txt. No task is sent.
# Usage: prep-p13.sh RUN CLEANUP_UTC      (e.g. p13l1 "2026-09-24 20:00:00")
# Output: $PREP/prep-result.env (W/V/D/U names + ids) for bind-p13.sh and the signed live inputs.
set -u
RUN=$1; CLEAN=$2; export AGENTDECK_PROFILE=campaign4
PREP=/home/bmosher/p13-prep-$RUN; PKG=/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
[ -e "$PREP" ] && { echo "prep root exists" >&2; exit 2; }
mkdir -p "$PREP/workdirs"; : > "$PREP/fixture-ids.txt"
agent-deck list --json > "$PREP/registry-before.json" 2>&1
# Cleanup fallback FIRST (calendar, AccuracySec=1s), exact IDs only; checked after arming.
cat > "$PREP/cleanup.sh" <<CL
#!/bin/bash
export AGENTDECK_PROFILE=campaign4
while read -r id; do [ -n "\$id" ] || continue; agent-deck session stop "\$id"; agent-deck session remove "\$id"; done < "$PREP/fixture-ids.txt" >> "$PREP/cleanup.log" 2>&1
CL
chmod 755 "$PREP/cleanup.sh"
systemd-run --user --unit="p13prep-cleanup-$RUN" --timer-property=AccuracySec=1s --on-calendar="$CLEAN UTC" "$PREP/cleanup.sh" || { echo "cleanup fallback not armed; nothing launched" >&2; exit 3; }
want=$(date -u -d "$CLEAN UTC" +%s)
systemctl --user show "p13prep-cleanup-$RUN.timer" -p TimersCalendar --timestamp=unix --value | grep -q "next_elapse=@$want" || { echo "cleanup timer not at $CLEAN" >&2; exit 3; }
out=$PREP/prep-result.env; : > "$out"
for spec in "W:worker:acp-go" "V:verifier:acp-go-deepseek" "D:director:acp-go" "U:duty:acp-go-controller"; do
  IFS=: read -r k role lane <<<"$spec"; name="p13-fixture-$role-$RUN"; mkdir -p "$PREP/workdirs/$role"
  agent-deck launch "$PREP/workdirs/$role" -t "$name" -cmd "/home/bmosher/.config/agent-deck/$lane" --idle-timeout=150m -json > "$PREP/$role.json" 2> "$PREP/$role.stderr"
  id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$PREP/$role.json" 2>/dev/null)
  [ -n "$id" ] || { echo "PREP FAIL: $role launch (see $PREP/$role.stderr); cleanup timer owns what exists" >&2; exit 3; }
  echo "$id" >> "$PREP/fixture-ids.txt"; printf '%s_NAME=%s\n%s_ID=%s\n' "$k" "$name" "$k" "$id" >> "$out"
done
agent-deck list --json > "$PREP/registry-after.json" 2>&1
echo "PREP PASS: $out (no task sent; binding is bind-p13.sh, read-only)"
