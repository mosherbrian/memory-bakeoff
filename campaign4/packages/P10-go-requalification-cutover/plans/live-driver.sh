#!/bin/bash
# P10 live qualification driver: one shot, L1-L7, evidence per case, cleanup in
# a trap. Plan for Tern's signature; nothing here ran on real systemd yet.
#
#   live-driver.sh INPUTS.env            run (only after Tern signs the inputs hash)
#   DRY=1 live-driver.sh INPUTS.env      print every command, run none (rehearsal)
#   live-driver.sh INPUTS.env cleanup    exact-ID cleanup only (the wall-stop runs this)
#
# Candidate: source 1341f0469fba (frozen), binary sha256 c1c49a29... (BIN_SHA).
# Every result line goes to $EV/results.tsv as CASE <tab> PASS|FAIL|INCOMPLETE <tab> detail.
# A case whose evidence is missing is INCOMPLETE, never PASS.
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}; DRY=${DRY:-0}
PKG=/home/bmosher/memory-bake-off/campaign4/packages/P10-go-requalification-cutover
PLANS=$PKG/plans
# shellcheck disable=SC1090
. "$INPUTS"
for v in RUN ROOT LIVE_DEADLINE PROFILE WAKE STREAMS BIN_SRC BIN_SHA UNITS_SRC W_NAME W_ID V_NAME V_ID D_NAME D_ID U_NAME U_ID; do
  val=${!v:-}
  if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
MAIN_IDS="0c933c75-1790000758 493c0317-1790000758 a79067ca-1790000758 56513e0e-1790000758"
for id in $W_ID $V_ID $D_ID $U_ID; do
  case " $MAIN_IDS " in *" $id "*) echo "main seat $id is forbidden" >&2; exit 2;; esac
done
P=fx$RUN                                   # project name: units agent-loop-$P*, ledger $ROOT/$P.db
A=$ROOT/bin/agent-loop
CFG=$ROOT/$P.json
C="--config $CFG"
U=agent-loop-$P.service
LU=agent-loop-liveness-$P
SD=/home/bmosher/.config/systemd/user
EV=${EV_DIR:-$PKG/live-$RUN}   # EV_DIR only for offline rehearsal
WALL=p10live-wallstop-$RUN
mkdir -p "$EV"

ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/driver.log"; }
run() { log "+ $*"; if [ "$DRY" = 1 ]; then return 0; fi; "$@" >>"$EV/driver.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
out() { log "+ $* (captured)"; if [ "$DRY" = 1 ]; then echo "DRY"; return 0; fi; "$@" 2>>"$EV/driver.log"; }
result() { printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$(ts)" "$3" | tee -a "$EV/results.tsv"; }
show() { out systemctl --user show "$U" --timestamp=unix -p ActiveState,SubState,Result,NRestarts,InvocationID,MainPID,ExecMainStartTimestamp; }
prop() { show | sed -n "s/^$1=//p"; }
state() { out cat "$ROOT/$P.db.liveness.json"; }
verdict() { state | python3 -c 'import json,sys; d=json.load(sys.stdin); print((d.get("last_verdict") or {}).get("state",""), d.get("last_check_at",""), (d.get("open") or {}).get("id",""))' 2>/dev/null; }
wakes() { if [ "$DRY" = 1 ]; then echo 0; return; fi; grep -c "$1" /home/bmosher/.local/share/agent-deck/wake-send.log; }
snap() { # case label: everything a reviewer needs, before and after
  { echo "## $1 $(ts)"; show; state; $A expose $C --json; tail -n 20 /home/bmosher/.local/share/agent-deck/wake-send.log;
    journalctl --user -u "$U" -u "$LU.service" --since "-10min" -o short-iso-precise --no-pager | tail -n 60; } >>"$EV/snapshots.txt" 2>&1; }
# wait_for LABEL SECONDS CMD...: poll every 5 s until CMD succeeds; 1 on timeout
wait_for() { local label=$1 limit=$2; shift 2; local t0; t0=$(date +%s)
  if [ "$DRY" = 1 ]; then log "wait_for $label ${limit}s: $*"; return 0; fi
  while ! "$@" >/dev/null 2>&1; do
    if [ $(( $(date +%s) - t0 )) -ge "$limit" ]; then log "timeout waiting for $label"; return 1; fi; sleep 5; done
  log "reached $label after $(( $(date +%s) - t0 ))s"; }
checks_since() { # count completed liveness runs since UTC time $1
  if [ "$DRY" = 1 ]; then echo 3; return; fi
  journalctl --user -u "$LU.service" --since "$1" -o cat --no-pager | grep -c '"verdict"'; }
quiet_window() { # LABEL EXPECTED_STATE: 3 min and at least 3 checks, all EXPECTED_STATE, no liveness wake
  local label=$1 want=$2 since w0; since=$(date -u '+%Y-%m-%d %H:%M:%S'); w0=$(wakes '\[agent-loop liveness\]')
  run sleep 185
  local n bad; n=$(checks_since "$since")
  bad=$( [ "$DRY" = 1 ] || journalctl --user -u "$LU.service" --since "$since" -o cat --no-pager | grep '"verdict"' | grep -vc "\"state\":\"$want\"" )
  if [ "$DRY" = 1 ]; then result "$label" DRY "3 min, >=3 checks, all $want"; return; fi
  if [ "$n" -ge 3 ] && [ "${bad:-0}" -eq 0 ] && [ "$(wakes '\[agent-loop liveness\]')" -eq "$w0" ]; then
    result "$label" PASS "$n checks in 185 s, all $want, no liveness wake"
  else result "$label" FAIL "$n checks, $bad not $want, liveness wakes $w0 -> $(wakes '\[agent-loop liveness\]')"; fi; }
task() { # template qid -> materialized file
  sed -e "s#{QID}#$2#g" -e "s#{ARTIFACTS}#$ROOT/art#g" -e "s#{BIN}#$A#g" -e "s#{CONFIG}#$CFG#g" "$PLANS/tasks/$1" > "$ROOT/tasks/$2-$1"; echo "$ROOT/tasks/$2-$1"; }
step() { $A expose $C --json 2>/dev/null | python3 -c "import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0])" 2>/dev/null; }
is_step() { [ "$(step "$1")" = "$2" ]; }
unit_is() { [ "$(prop ActiveState)" = "$1" ]; }
new_invocation() { [ "$(prop InvocationID)" != "$1" ] && unit_is active; }
state_is() { verdict | grep -q "^$1 "; }

cleanup() {
  trap - EXIT
  log "cleanup (exact IDs)"
  mkdir -p "$EV/archive"
  [ "$DRY" = 1 ] || cp -a "$ROOT"/. "$EV/archive/" 2>/dev/null
  run systemctl --user stop "$LU.timer" "$LU.service" "$U"
  for t in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do run systemctl --user stop "$t"; done
  run systemctl --user reset-failed "agent-loop-$P*" "$LU*"
  run rm -f "$SD/$U" "$SD/$LU.service" "$SD/$LU.timer"
  run rm -rf "$SD/$U.d"
  run systemctl --user daemon-reload
  for id in $W_ID $V_ID $D_ID $U_ID; do run agent-deck session stop "$id"; run agent-deck session remove "$id"; done
  run systemctl --user stop "$WALL.timer"
  log "cleanup done"
}
if [ "$MODE" = cleanup ]; then cleanup; exit 0; fi
trap cleanup EXIT

# ---------------------------------------------------------------- setup
log "P10 live $RUN, inputs sha256 $(sha256sum "$INPUTS" | cut -d' ' -f1)"
now=$(date +%s); dl=$(date -d "$LIVE_DEADLINE" +%s)
if [ "$dl" -le "$now" ]; then log "live deadline $LIVE_DEADLINE already passed"; result SETUP INCOMPLETE "deadline passed"; exit 3; fi
# Bounded wall stop, armed before any task: cleanup runs at the live deadline even if this shell dies.
run systemd-run --user --unit="$WALL" --on-active=$(( dl - now ))s /bin/bash "$PLANS/live-driver.sh" "$INPUTS" cleanup
if [ -e "$ROOT" ] && [ "$DRY" != 1 ]; then result SETUP INCOMPLETE "private root $ROOT exists"; exit 3; fi
run mkdir -p "$ROOT/bin" "$ROOT/art" "$ROOT/claims" "$ROOT/tasks"
run install -m 755 "$BIN_SRC" "$A"
if [ "$DRY" != 1 ] && [ "$(sha256sum "$A" | cut -d' ' -f1)" != "$BIN_SHA" ]; then result SETUP FAIL "binary hash mismatch"; exit 3; fi
[ "$DRY" = 1 ] && log "+ write config $CFG" || python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "$P", "profile": "$PROFILE", "wake": "$WAKE", "db": "$ROOT/$P.db", "stream_dir": "$STREAMS",
  "claims_dir": "$ROOT/claims", "artifacts_dir": "$ROOT/art", "director": "$D_NAME", "duty": "$U_NAME",
  "seats": {"$W_NAME": "$W_ID", "$V_NAME": "$V_ID", "$D_NAME": "$D_ID", "$U_NAME": "$U_ID"},
  "bin": "$A", "unit": "$U"}, open(sys.argv[1], "w"), indent=1)
PY
sub="s#%h/.local/bin/agent-loop#$A#g; s#%h/.config/agent-loop/%i.json#$CFG#g; s#agent-loop %i#agent-loop $P#g; s#%i#$P#g"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop@.service' > '$SD/$U'"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop-liveness@.service' > '$SD/$LU.service'"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop-liveness@.timer' > '$SD/$LU.timer'"
run grep -c "$A" "$SD/$U" "$SD/$LU.service"
run systemctl --user daemon-reload
run "$A" check $C || { result SETUP FAIL "seat binding check failed"; exit 3; }
for seat in "$D_NAME:$D_ID" "$U_NAME:$U_ID"; do run "$WAKE" "${seat#*:}" "$(cat "$PLANS/tasks/ack.md")"; done
run systemctl --user start "$U" "$LU.timer"
wait_for "first pass" 60 state_is ok || wait_for "first rest" 60 state_is rest
snap SETUP

# ---------------------------------------------------------------- L1 positive handoff, restart, decide
Q=L1-$RUN; log "L1 onset"
run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task l-worker.md "$Q")" --verify-task "@$(task l-verify.md "$Q")" --duration 10m --verify-window 10m
if wait_for "L1 decision" 600 is_step "$Q" decision; then
  w1=$(wakes "$W_ID"); v1=$(wakes "$V_ID")
  inv=$(prop InvocationID); run systemctl --user restart "$U"; wait_for "L1 restart pass" 90 new_invocation "$inv"
  run "$A" decide $C --qid "$Q" --kind question_answered --ref "P10-live-$RUN-L1" --reason "live witness"
  if is_step "$Q" closed && [ "$(wakes "$W_ID")" = "$w1" ] && [ "$(wakes "$V_ID")" = "$v1" ]; then result L1 PASS "closed; one dispatch per seat across restart"
  else result L1 FAIL "step $(step "$Q"); worker wakes $w1->$(wakes "$W_ID"), verifier $v1->$(wakes "$V_ID")"; fi
else result L1 INCOMPLETE "no verdict within 600 s (step $(step "$Q"))"; fi
snap L1
wait_for "L1 settled" 120 state_is rest
quiet_window L5-rest rest

# ---------------------------------------------------------------- L2 kill during work
Q=L2-$RUN; run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task l-noclaim-worker.md "$Q")" --verify-task "@$(task l-verify.md "$Q")" --duration 15m --verify-window 5m
wait_for "L2 worker step" 30 is_step "$Q" worker
w1=$(wakes "$W_ID"); r1=$(prop NRestarts); inv=$(prop InvocationID)
log "L2 onset: SIGKILL"; run systemctl --user kill -s KILL "$U"
if wait_for "L2 restarted" 30 new_invocation "$inv" && wait_for "L2 pass" 60 state_is ok; then
  if [ "$(prop NRestarts)" -gt "$r1" ] && [ "$(wakes "$W_ID")" = "$w1" ] && journalctl --user -u "$U" --since "-3min" -o cat --no-pager | grep -q held-awaiting-receipt; then
    result L2 PASS "restarted by systemd, outbox held, no resend"
  else result L2 FAIL "restarts $r1->$(prop NRestarts), worker wakes $w1->$(wakes "$W_ID")"; fi
else result L2 FAIL "no restart/pass within bounds"; fi
snap L2

# ---------------------------------------------------------------- L3a hang: watchdog
inv=$(prop InvocationID); log "L3a onset: SIGSTOP main pid"; run kill -STOP "$(prop MainPID)"
if wait_for "L3a watchdog restart" 110 new_invocation "$inv"; then
  journalctl --user -u "$U" --since "-3min" -o cat --no-pager | grep -qi watchdog && result L3a PASS "watchdog killed and systemd restarted run" || result L3a FAIL "restart without a watchdog line"
else result L3a FAIL "no watchdog restart within 110 s"; fi
wait_for "L3a pass" 90 state_is ok; snap L3a

# ---------------------------------------------------------------- L7c causal pre-first-pass window
# The OS fault: a drop-in makes the unit's main process sleep 40 s before exec'ing run
# (same PID, same InvocationID), so the window before the first pass is controlled, not raced.
run mkdir -p "$SD/$U.d"
run sh -c "printf '[Service]\nExecStart=\nExecStart=/bin/sh -c \"sleep 40; exec $A run --config $CFG\"\nTimeoutStartSec=120\n' > '$SD/$U.d/delay.conf'"
run systemctl --user daemon-reload; inv=$(prop InvocationID); log "L7c onset: restart with 40 s delay"; run systemctl --user restart --no-block "$U"
wait_for "L7c new invocation" 20 sh -c "[ \"\$(systemctl --user show $U -p InvocationID --value)\" != '$inv' ]"
run systemctl --user start "$LU.service"   # an outside check inside the window
if state_is starting; then s1=PASS; else s1="FAIL($(verdict))"; fi
wait_for "L7c first pass of the new run" 90 state_is ok; run systemctl --user start "$LU.service"
if [ "$s1" = PASS ] && state_is ok; then result L7c PASS "starting (quiet, not recovered) inside the window; ok after the new run's pass"; else result L7c FAIL "window $s1, after $(verdict)"; fi
run rm -f "$SD/$U.d/delay.conf"; run systemctl --user daemon-reload; snap L7c

# ---------------------------------------------------------------- L3b hang seen by the outside check (watchdog off)
run sh -c "printf '[Service]\nWatchdogSec=0\n' > '$SD/$U.d/nowatchdog.conf'"; run systemctl --user daemon-reload; run systemctl --user restart "$U"
wait_for "L3b pass" 90 state_is ok
d1=$(wakes "$U_ID"); log "L3b onset: SIGSTOP main pid, no watchdog"; run kill -STOP "$(prop MainPID)"; t0=$(date +%s)
if wait_for "L3b hung" 180 state_is hung; then
  el=$(( $(date +%s) - t0 )); [ "$(wakes "$U_ID")" -gt "$d1" ] && result L3b PASS "hung after ${el}s (bound 180), duty woken" || result L3b FAIL "hung but duty not woken"
else result L3b FAIL "not hung within 180 s"; fi
run kill -CONT "$(prop MainPID)"; run rm -f "$SD/$U.d/nowatchdog.conf"; run systemctl --user daemon-reload; run systemctl --user restart "$U"
wait_for "L3b recovered" 150 state_is ok; snap L3b

# ---------------------------------------------------------------- L4a restart loop, owned escalation with duty's ack
run sh -c "printf '[Service]\nExecStart=\nExecStart=$A run --config /nonexistent-$RUN.json\n' > '$SD/$U.d/fail.conf'"; run systemctl --user daemon-reload
log "L4a onset: failing start"; run systemctl --user restart "$U"
if wait_for "L4a start limit" 120 sh -c "systemctl --user show $U -p Result --value | grep -q start-limit-hit" && wait_for "L4a restart-loop verdict" 60 state_is restart-loop; then
  if wait_for "L4a duty ack recorded" 300 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));a=d[\"open\"][\"ack\"];assert a[\"by\"]==\"$U_NAME\" and a[\"next_action\"] and a[\"response_deadline\"]'"; then
    run rm -f "$SD/$U.d/fail.conf"; run systemctl --user daemon-reload; run systemctl --user reset-failed "$U"; run systemctl --user start "$U"
    wait_for "L4a recovered" 150 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));assert d.get(\"open\") is None and d[\"history\"][-1][\"outcome\"]==\"recovered\"'" \
      && result L4a PASS "restart-loop -> duty ack (owner/next/deadline) -> recovered on fresh pass" || result L4a FAIL "no recovery after ack"
  else result L4a FAIL "duty never acknowledged"; fi
else result L4a FAIL "no start-limit/restart-loop within bounds"; fi
run rm -f "$SD/$U.d/fail.conf"; run systemctl --user daemon-reload; run systemctl --user reset-failed "$U"; run systemctl --user start "$U"
wait_for "L4a settled" 90 state_is rest; snap L4a

# ---------------------------------------------------------------- L7a damaged state, L7b future pass (real checker path)
run sh -c "printf '{bad-$RUN' > '$ROOT/$P.db.liveness.json'"; u1=$(wakes "$U_ID")
wait_for "L7a alarm" 60 sh -c "ls $ROOT/$P.db.liveness.json.damaged-*.json"
since=$(date -u '+%Y-%m-%d %H:%M:%S'); run sleep 140
if [ "$DRY" = 1 ] || { grep -q "{bad-$RUN" "$ROOT"/$P.db.liveness.json.damaged-*.json && [ "$(wakes "$U_ID")" -eq $(( u1 + 1 )) ] && [ "$(checks_since "$since")" -ge 3 ]; }; then result L7a PASS "bytes preserved, duty woken once over >=3 checks"; else result L7a FAIL "copy/wakes $u1->$(wakes "$U_ID")"; fi
snap L7a
# L7a's incident needs an ack before it can close: the duty seat has the standing ack instruction.
wait_for "L7a closed after ack" 300 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));assert d.get(\"open\") is None'"
# The unit must stay active (a stopped unit reads "down" before the pass is looked at) and
# run must not overwrite the injected pass: pause run with SIGSTOP (well under the 90 s watchdog).
mp=$(prop MainPID); log "L7b onset: SIGSTOP run, write a pass 10 min in the future"; run kill -STOP "$mp"
run python3 -c "import sqlite3,json,datetime;c=sqlite3.connect('$ROOT/$P.db');p=json.loads(c.execute(\"select value from driver_kv where key='loop-pass'\").fetchone()[0]);p['at']=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ');c.execute(\"update driver_kv set value=? where key='loop-pass'\",(json.dumps(p),));c.commit()"
run systemctl --user start "$LU.service"
state_is unknown && state | grep -q "in the future" && result L7b PASS "future pass -> unknown alarm" || result L7b FAIL "$(verdict)"
run kill -CONT "$mp"; wait_for "L7b recovered" 150 state_is rest; snap L7b

# ---------------------------------------------------------------- L6 timeout while run is down + L5 stopped quiet
Q=L6-$RUN; run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task l-noclaim-worker.md "$Q")" --verify-task "@$(task l-verify.md "$Q")" --duration 2m --verify-window 5m
wait_for "L6 worker step" 30 is_step "$Q" worker
c1=$(wakes "$W_ID"); dd1=$(wakes "$D_ID"); tstop=$(date -u '+%Y-%m-%d %H:%M:%S')
log "L5 onset: agent-loop stop"; run "$A" stop $C
wait_for "L5 run exited" 60 sh -c "systemctl --user show $U -p ExecMainStatus --value | grep -qx 64"
st=$(prop ActiveState)
log "L5: stray start while the marker exists"; run systemctl --user start "$U"; src=$?
run sleep 20   # longer than RestartSec: a restart storm would show by now
sched=$( [ "$DRY" = 1 ] && echo 0 || journalctl --user -u "$U" --since "$tstop" -o cat --no-pager | grep -c "Scheduled restart" )
[ "$sched" -eq 0 ] && [ -e "$ROOT/$P.db.stop" ] && [ "$(prop ActiveState)" != active ] \
  && result L5-stray PASS "exit 64 (state $st); stray start rc=$src (recorded, not assumed 0); marker kept; no scheduled restart" \
  || result L5-stray FAIL "scheduled restarts $sched, state $(prop ActiveState), marker $(ls "$ROOT/$P.db.stop" 2>&1)"
quiet_window L5-stopped stopped    # the L6 deadline (2 min) falls inside this window
if [ "$DRY" = 1 ] || { [ "$(wakes "$W_ID")" -eq $(( c1 + 1 )) ] && [ "$(wakes "$D_ID")" -eq $(( dd1 + 1 )) ] && journalctl --user -u "agent-loop-$P-$Q-w1.service" -o cat --no-pager | grep -q interrupted; }; then
  run systemctl --user start "agent-loop-$P-$Q-w1.service"   # replay the callback
  if [ "$DRY" = 1 ] || { [ "$(wakes "$W_ID")" -eq $(( c1 + 1 )) ] && journalctl --user -u "agent-loop-$P-$Q-w1.service" -o cat --no-pager | tail -n 3 | grep -q already-handled; }; then
    result L6 PASS "interrupted once while run was stopped: one /cancel, one director wake; replay already-handled"
  else result L6 FAIL "replay repeated effects"; fi
else result L6 FAIL "cancel/director wakes $c1->$(wakes "$W_ID") $dd1->$(wakes "$D_ID")"; fi
run "$A" start $C; wait_for "L5 resumed" 90 sh -c "systemctl --user is-active $U"; snap L5-L6

# ---------------------------------------------------------------- L4b duty unavailable (last: it stops the duty seat)
run agent-deck session stop "$U_ID"
run sh -c "printf '[Service]\nExecStart=\nExecStart=$A run --config /nonexistent-$RUN.json\n' > '$SD/$U.d/fail.conf'"; run systemctl --user daemon-reload
d1=$(wakes "$D_ID"); log "L4b onset: failing start, duty seat stopped"; run systemctl --user restart "$U"
if wait_for "L4b restart-loop" 180 state_is restart-loop && [ "$DRY" = 1 -o "$(wakes "$D_ID")" -gt "$d1" ]; then
  wait_for "L4b director ack" 300 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));assert d[\"open\"][\"ack\"][\"by\"]==\"$D_NAME\"'" \
    && result L4b PASS "duty wake failed -> director woken in the same check -> director ack recorded" || result L4b FAIL "no director ack"
else result L4b FAIL "director not woken"; fi
run rm -f "$SD/$U.d/fail.conf"; run systemctl --user daemon-reload; snap L4b

log "all cases run; results in $EV/results.tsv"
# cleanup runs from the trap
