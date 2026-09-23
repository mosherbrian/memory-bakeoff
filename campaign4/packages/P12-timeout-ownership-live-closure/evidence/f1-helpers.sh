#!/bin/bash
# F1 offline: the driver's REAL helper functions (extracted unchanged from DRIVER, ts() through
# state_is()), run non-DRY on fixture state files. Usage: f1-helpers.sh DRIVER
set -u
DRIVER=$1; X=$(mktemp -d /tmp/p11-f1-XXXX); EV=$X/ev; ROOT=$X/root; P=fx; DRY=0; mkdir -p $EV $ROOT
U=agent-loop-fx.service; A=/bin/false; C=""
eval "$(sed -n '/^ts()/,/^state_is()/p' "$DRIVER")"
ok=0; bad=0
chk() { if [ "$2" = "$3" ]; then echo "PASS  $1: '$2'"; ok=$((ok+1)); else echo "FAIL  $1: got '$2' want '$3'"; bad=$((bad+1)); fi; }
fx() { printf '%s' "$1" > $ROOT/$P.db.liveness.json; }
echo "== driver $(sha256sum "$DRIVER" | cut -c1-16)"
for s in rest ok starting unknown; do
  fx "{\"last_verdict\": {\"state\": \"$s\", \"why\": \"fixture\"}, \"last_check_at\": \"2026-09-23T15:00:00Z\"}"
  chk "state() stdout is only the file" "$(state | head -c 1)" "{"
  chk "verdict on valid $s" "$(verdict | cut -d' ' -f1)" "$s"
  state_is "$s"; chk "state_is $s on $s" "$?" 0
done
fx '{"last_verdict": {"state": "ok"}, "last_check_at": "2026-09-23T15:00:00Z", "open": {"id": "L20260923T150000Z"}}'
chk "verdict carries the open incident id" "$(verdict | cut -d' ' -f3)" "L20260923T150000Z"
state_is rest; chk "NEGATIVE: valid JSON, state ok, is not rest" "$?" 1
for name in malformed empty missing no-verdict; do
  case $name in malformed) fx '{bad';; empty) fx '';; missing) rm -f $ROOT/$P.db.liveness.json;; no-verdict) fx '{"last_check_at": "x"}';; esac
  v=$(verdict); rc=$?
  chk "$name: verdict rc" "$rc" 1
  chk "$name: verdict says PARSE-ERROR, never a state" "$(echo "$v" | cut -d' ' -f1)" PARSE-ERROR
  state_is rest; chk "$name: state_is rest is false" "$?" 1
done
: > $EV/results.tsv
wait_for "fixture never rest" 6 state_is rest; chk "failed required wait returns 1" "$?" 1
chk "failed wait wrote an INCOMPLETE row" "$(cut -f1,2 $EV/results.tsv | tr '\t' ' ')" "wait:fixture never rest INCOMPLETE"
chk "diagnostic kept in driver.log (one per failed read)" "$(( $(grep -c 'state file unusable' $EV/driver.log) >= 4 ))" 1
echo "== $ok PASS, $bad FAIL"; [ $bad -eq 0 ]
