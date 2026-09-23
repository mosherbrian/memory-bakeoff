#!/bin/bash
# P12 live qualification driver (P11 driver + P12 section D/E): one shot, L1-L7,
# evidence per case, cleanup in a trap. Plan for Tern's signature; nothing here ran on real systemd yet.
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
PKG=/home/bmosher/memory-bake-off/campaign4/packages/P12-timeout-ownership-live-closure
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
# Deadline guard: a missing or unparseable deadline fails closed before any effect.
DL_EPOCH=$(date -u -d "$LIVE_DEADLINE" +%s 2>/dev/null) || { echo "LIVE_DEADLINE '$LIVE_DEADLINE' is not a valid time" >&2; exit 2; }
# R1: every agent-deck call (driver, children, detached wall) uses the declared profile.
export AGENTDECK_PROFILE="$PROFILE"
if [ "$(printf '%s\n' "$W_ID" "$V_ID" "$D_ID" "$U_ID" | sort -u | wc -l)" -ne 4 ] || [ "$(printf '%s\n' "$W_NAME" "$V_NAME" "$D_NAME" "$U_NAME" | sort -u | wc -l)" -ne 4 ]; then
  echo "fixture IDs and names must be four distinct pairs" >&2; exit 2; fi
P=fx$RUN                                   # project name: units agent-loop-$P*, ledger $ROOT/$P.db
A=$ROOT/bin/agent-loop
CFG=$ROOT/$P.json
C="--config $CFG"
U=agent-loop-$P.service
LU=agent-loop-liveness-$P
SD=/home/bmosher/.config/systemd/user
EV=${EV_DIR:-$PKG/live-$RUN}   # EV_DIR only for offline rehearsal
WALL=p12live-wallstop-$RUN
SCOPE=p12live-driver-$RUN   # F2: the driver and every child run in this owned scope
mkdir -p "$EV"

ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/driver.log"; }
_now() { date +%s; }
# Deadline guard. Every path that starts new work calls it: run(), task(), the config write.
# At or past the deadline (host clock) it refuses the work, writes DEADLINE INCOMPLETE and exits
# (the EXIT trap then tears down). Teardown (cleanup, the wall) sets TEARDOWN=1 and is not refused.
# It refuses new work when it sees expiry; work admitted just before may still end after it
# (the owned-scope wall stops that). out() is read-only: only show() and state() use it.
guard() { [ -n "${TEARDOWN:-}" ] || [ "$DRY" = 1 ] || [ "$(_now)" -lt "$DL_EPOCH" ] && return 0
  echo "$(ts) DEADLINE: refused new work (deadline $LIVE_DEADLINE): $*" >>"$EV/driver.log"
  result DEADLINE INCOMPLETE "refused at $(ts), deadline $LIVE_DEADLINE: $*"; exit 3; }
run() { guard "$@"; log "+ $*"; if [ "$DRY" = 1 ]; then return 0; fi; "$@" >>"$EV/driver.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
out() { echo "$(ts) + $* (captured)" >>"$EV/driver.log"; if [ "$DRY" = 1 ]; then echo "DRY"; return 0; fi; "$@" 2>>"$EV/driver.log"; }
# F1: a DRY (construction) run never records PASS or FAIL: every row is DRY.
result() { local st=$2; [ "$DRY" = 1 ] && st=DRY; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/results.tsv"; }
show() { out systemctl --user show "$U" --timestamp=unix -p ActiveState,SubState,Result,NRestarts,InvocationID,MainPID,ExecMainStartTimestamp; }
prop() { show | sed -n "s/^$1=//p"; }
state() { out cat "$ROOT/$P.db.liveness.json"; }
# verdict: "STATE CHECKED_AT INCIDENT" from the state file; unreadable or malformed state
# prints "PARSE-ERROR ..." (the reason also goes to driver.log) and returns 1: never a state.
verdict() { state | python3 -c '
import json,sys
try:
    d = json.load(sys.stdin); s = (d.get("last_verdict") or {}).get("state", "")
    assert isinstance(s, str) and s, "no last_verdict.state"
except Exception as e:
    print("PARSE-ERROR", type(e).__name__); print("verdict: state file unusable:", e, file=sys.stderr); sys.exit(1)
print(s, d.get("last_check_at", ""), (d.get("open") or {}).get("id", ""))' 2>>"$EV/driver.log"; }
wakes() { if [ "$DRY" = 1 ]; then echo 0; return; fi; grep -c "$1" /home/bmosher/.local/share/agent-deck/wake-send.log; }
snap() { # case label: everything a reviewer needs, before and after
  { echo "## $1 $(ts)"; show; state; $A expose $C --json; tail -n 20 /home/bmosher/.local/share/agent-deck/wake-send.log;
    journalctl --user -u "$U" -u "$LU.service" --since "-10min" -o short-iso-precise --no-pager | tail -n 60; } >>"$EV/snapshots.txt" 2>&1; }
# wait_for LABEL SECONDS CMD...: poll every 5 s until CMD succeeds; 1 on timeout
wait_for() { local label=$1 limit=$2; shift 2; local t0; t0=$(date +%s)
  if [ "$DRY" = 1 ]; then log "wait_for $label ${limit}s: $*"; return 0; fi
  while ! "$@" >/dev/null 2>&1; do
    if [ $(( $(date +%s) - t0 )) -ge "$limit" ]; then log "timeout waiting for $label"; result "wait:$label" INCOMPLETE "not reached in ${limit}s"; return 1; fi; sleep 5; done
  log "reached $label after $(( $(date +%s) - t0 ))s"; }
checks_since() { # count completed liveness runs since $1 (@EPOCH: journalctl reads zoneless times as LOCAL)
  if [ "$DRY" = 1 ]; then echo 3; return; fi
  journalctl --user -u "$LU.service" --since "$1" -o cat --no-pager | grep -c '"verdict"'; }
quiet_window() { # LABEL EXPECTED_STATE [SECONDS=185]: >=3 checks, all EXPECTED_STATE, no liveness wake
  local label=$1 want=$2 secs=${3:-185} since w0; since=@$(date +%s); w0=$(wakes '\[agent-loop liveness\]')
  run sleep "$secs"
  local n bad; n=$(checks_since "$since")
  bad=$( [ "$DRY" = 1 ] || journalctl --user -u "$LU.service" --since "$since" -o cat --no-pager | grep '"verdict"' | grep -vc "\"state\":\"$want\"" )
  if [ "$DRY" = 1 ]; then result "$label" DRY "${secs} s, >=3 checks, all $want"; return; fi
  if [ "$n" -ge 3 ] && [ "${bad:-0}" -eq 0 ] && [ "$(wakes '\[agent-loop liveness\]')" -eq "$w0" ]; then
    result "$label" PASS "$n checks in $secs s, all $want, no liveness wake"
  else result "$label" FAIL "$n checks, $bad not $want, liveness wakes $w0 -> $(wakes '\[agent-loop liveness\]')"; fi; }
task() { # template qid -> materialized file
  guard "task $1 $2"; sed -e "s#{QID}#$2#g" -e "s#{ARTIFACTS}#$ROOT/art#g" -e "s#{BIN}#$A#g" -e "s#{CONFIG}#$CFG#g" "$PLANS/tasks/$1" > "$ROOT/tasks/$2-$1"; echo "$ROOT/tasks/$2-$1"; }
step() { $A expose $C --json 2>/dev/null | python3 -c "import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0])" 2>/dev/null; }
is_step() { [ "$(step "$1")" = "$2" ]; }
unit_is() { [ "$(prop ActiveState)" = "$1" ]; }
new_invocation() { [ "$(prop InvocationID)" != "$1" ] && unit_is active; }
state_is() { verdict | grep -q "^$1 "; }
state_in() { local s w; s=$(verdict | cut -d' ' -f1); for w; do [ "$s" = "$w" ] && return 0; done; return 1; }
# R1: the registry (agent-deck list, declared profile) must hold exactly these four fixtures:
# each ID once, with its declared title, in $PROFILE, not archived. Prints the problems; rc 1 if any.
registry_check() { agent-deck list --json 2>>"$EV/driver.log" | python3 -c '
import json, sys
want = dict(zip(sys.argv[2::2], sys.argv[3::2])); prof = sys.argv[1]; bad = []
try:
    d = json.load(sys.stdin); d = d if isinstance(d, list) else d.get("sessions", [])
except Exception as e:
    print("registry unreadable:", e); sys.exit(1)
for i, name in want.items():
    rows = [r for r in d if r.get("id") == i]
    if len(rows) != 1: bad.append("%s: %d registry rows" % (i, len(rows))); continue
    r = rows[0]
    if r.get("title") != name: bad.append("%s: title %r, declared %r" % (i, r.get("title"), name))
    if r.get("profile", prof) != prof: bad.append("%s: profile %r, declared %r" % (i, r.get("profile"), prof))
    if r.get("archived"): bad.append("%s: archived" % i)
print("; ".join(bad) or "ok"); sys.exit(1 if bad else 0)' "$PROFILE" "$W_ID" "$W_NAME" "$V_ID" "$V_NAME" "$D_ID" "$D_NAME" "$U_ID" "$U_NAME"; }
seat_status() { # ID -> registry status, or "absent"
  agent-deck list --json 2>>"$EV/driver.log" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin); d = d if isinstance(d, list) else d.get("sessions", [])
except Exception:
    print("unreadable"); sys.exit()
print(next((r.get("status", "") for r in d if r.get("id") == sys.argv[1]), "absent"))' "$1"; }
# R2: a seat counts as stopped only when the registry says so after the stop command succeeded.
# L6 timing, predeclared class: EXPLICIT (the deadline is known). Detection = the settled timeout's
# host time (status timeout.at) minus the authorized deadline, bound 30 s. Ownership = the recorded
# acknowledgement's host time (status timeout.ack.at, by the director or duty) minus the deadline, bound
# 90 s (30 + 60). A sent wake is never ownership. Timer lateness counts against detection; it is never
# reclassified as suspicion. No settled timeout or no deadline: INCOMPLETE; no acknowledgement: FAIL.
l6_eval() { # DEADLINE SETTLED_AT ACK_AT -> "PASS|FAIL|INCOMPLETE detail"
  python3 -c '
import sys, datetime as D
def t(x):
    try: return D.datetime.fromisoformat(x.replace("Z", "+00:00"))
    except Exception: return None
dl, it, ak = (t(a) for a in sys.argv[1:4])
if dl is None or it is None: print("INCOMPLETE missing timestamp(s): deadline=%s settled=%s" % tuple(sys.argv[1:3])); sys.exit()
det = (it - dl).total_seconds()
if ak is None: print("FAIL explicit: detection %.1fs (bound 30); NO acknowledgement recorded (ownership bound 90)" % det); sys.exit()
own = (ak - dl).total_seconds()
ok = 0 <= det <= 30 and det <= own <= 90
print("%s explicit: detection %.1fs (bound 30), acknowledged ownership %.1fs (bound 90) from deadline %s" % ("PASS" if ok else "FAIL", det, own, sys.argv[1]))' "$@"; }
l6_timing() {
  if [ "$DRY" = 1 ]; then result L6-timing DRY "deadline/settled/ack timestamps"; return; fi
  local tj r
  wait_for "L6 acknowledged" 120 sh -c "$A status $C --json | python3 -c \"import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert (p.get('timeout') or {}).get('ack')\""
  tj=$($A status $C --json 2>>"$EV/driver.log" | python3 -c "import json,sys; print(json.dumps([p.get('timeout') or {} for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]))" 2>>"$EV/driver.log")
  printf '{"deadline": "%s", "callback_start": "%s", "timeout": %s}\n' "$l6dl" "$(systemctl --user show "agent-loop-$P-$Q-w1.service" -p ExecMainStartTimestamp --value 2>&1)" "${tj:-null}" > "$EV/l6-timing.json"
  local st ak
  st=$(printf '%s' "$tj" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("at", ""))
except Exception: print("")')
  ak=$(printf '%s' "$tj" | python3 -c 'import json,sys
try: print((json.load(sys.stdin).get("ack") or {}).get("at", ""))
except Exception: print("")')
  r=$(l6_eval "$l6dl" "$st" "$ak")
  result L6-timing "${r%% *}" "${r#* } ($EV/l6-timing.json)"; }
stop_seat() { run agent-deck session stop "$1" || return 1; [ "$DRY" = 1 ] && return 0; [ "$(seat_status "$1")" = stopped ]; }

cleanup() {
  trap - EXIT; TEARDOWN=1
  if ! mkdir "$EV/cleanup.lock" 2>/dev/null; then log "cleanup already ran (lock $EV/cleanup.lock)"; return 0; fi
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
  # R2: outcomes are checked, not assumed: every fixture gone from the registry, no unit of this run active.
  local left="" id u
  if [ "$DRY" != 1 ]; then
    for id in $W_ID $V_ID $D_ID $U_ID; do st=$(seat_status "$id"); [ "$st" = absent ] || left="$left seat $id ($st);"; done
    for u in "$LU.timer" "$LU.service" "$U" $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do
      [ "$(systemctl --user is-active "$u" 2>/dev/null)" = active ] && left="$left unit $u active;"; done
  fi
  if [ -n "$left" ]; then result CLEANUP FAIL "unresolved:$left"; log "cleanup INCOMPLETE:$left"; return 1; fi
  log "cleanup done"
}
# E: the wall is a calendar timer at the deadline (explicit UTC); daemon-reload restarts --on-active
# countdowns (P12 evidence/e-reload-timers-run1.txt) but not calendar times. Its next elapse is read
# as epoch seconds (TimersCalendar next_elapse=@N; NextElapseUSecRealtime prints a local date even
# with --timestamp=unix) and must equal the deadline; checked when armed and after every daemon-reload.
wall_next() { systemctl --user show "$WALL.timer" -p TimersCalendar --timestamp=unix --value 2>/dev/null | grep -o 'next_elapse=@[0-9]*' | cut -d= -f2; }
wall_ok() { [ "$(wall_next)" = "@$DL_EPOCH" ]; }
reload() { run systemctl --user daemon-reload || return 1; [ "$DRY" = 1 ] || wall_ok || { result WALL FAIL "after daemon-reload the wall reads '$(wall_next)', not @$DL_EPOCH"; exit 3; }; }
# end of helpers
if [ "$MODE" = cleanup ]; then
  TEARDOWN=1
  # The wall (or an operator): first stop the driver's owned scope, which ends the driver and
  # every child it started (systemd kills the whole cgroup), and only then clean up.
  if [ "$(systemctl --user is-active "$SCOPE.scope" 2>/dev/null)" = active ]; then
    log "WALLSTOP: stopping $SCOPE.scope (driver and children)"; systemctl --user stop "$SCOPE.scope"
    result WALLSTOP INCOMPLETE "live deadline $LIVE_DEADLINE reached; driver scope stopped before cleanup"
  fi
  cleanup; exit 0
fi
# R1: registry preflight before any unit or seat effect (read-only).
if [ "$DRY" != 1 ]; then
  why=$(registry_check) || { result SETUP FAIL "fixture registry check in profile $PROFILE: $why"; exit 3; }
  log "registry: four fixtures confirmed in profile $PROFILE"
fi
# F2: run inside an owned scope (validated below by cgroup membership, never a PID file).
if [ "$DRY" != 1 ] && [ "${P12_IN_SCOPE:-}" != "$SCOPE" ]; then
  [ "$(_now)" -lt "$DL_EPOCH" ] || { result SETUP INCOMPLETE "live deadline $LIVE_DEADLINE already passed: no effect started"; exit 3; }
  # Not exec: if systemd-run cannot create the scope, say so instead of ending silently.
  env P12_IN_SCOPE="$SCOPE" systemd-run --user --scope --quiet --unit="$SCOPE" -- /bin/bash "$0" "$@"; rc=$?
  [ -e "$EV/scope-entered.$SCOPE" ] || { result SETUP FAIL "owned scope $SCOPE not created (systemd-run rc=$rc): no effect started"; exit 3; }
  exit $rc
fi
if [ "$DRY" != 1 ] && ! grep -q "/$SCOPE.scope\$" /proc/$$/cgroup; then result SETUP FAIL "driver is not in $SCOPE.scope"; exit 3; fi
[ "$DRY" = 1 ] || touch "$EV/scope-entered.$SCOPE"
# A stop of the scope (the wall) must not start a second cleanup from inside it.
trap 'trap - EXIT; log "driver terminated by signal (wall stop)"; exit 143' TERM

# ---------------------------------------------------------------- setup
log "P12 live $RUN, inputs sha256 $(sha256sum "$INPUTS" | cut -d' ' -f1)"
now=$(date +%s); dl=$(date -d "$LIVE_DEADLINE" +%s)
if [ "$dl" -le "$now" ]; then log "live deadline $LIVE_DEADLINE already passed"; result SETUP INCOMPLETE "deadline passed"; exit 3; fi
# Bounded wall stop, armed before any task: cleanup runs at the live deadline even if this shell dies.
run systemd-run --user --unit="$WALL" --timer-property=AccuracySec=1s --on-calendar="$(date -u -d @$DL_EPOCH '+%Y-%m-%d %H:%M:%S') UTC" --setenv=PATH="$PATH" --setenv=AGENTDECK_PROFILE="$PROFILE" ${EV_DIR:+--setenv=EV_DIR="$EV_DIR"} /bin/bash "$PLANS/live-driver.sh" "$INPUTS" cleanup \
  || { result SETUP FAIL "wall-stop not armed: no effect started"; exit 3; }
if [ "$DRY" != 1 ] && { [ "$(systemctl --user is-active "$WALL.timer")" != active ] || ! wall_ok; }; then result SETUP FAIL "wall-stop timer $WALL.timer not active at $LIVE_DEADLINE ($(wall_next)): no effect started"; exit 3; fi
trap cleanup EXIT   # armed and verified: from here every exit cleans up exact IDs once
if [ -e "$ROOT" ] && [ "$DRY" != 1 ]; then result SETUP INCOMPLETE "private root $ROOT exists"; exit 3; fi
run mkdir -p "$ROOT/bin" "$ROOT/art" "$ROOT/claims" "$ROOT/tasks"
run install -m 755 "$BIN_SRC" "$A"
if [ "$DRY" != 1 ] && [ "$(sha256sum "$A" | cut -d' ' -f1)" != "$BIN_SHA" ]; then result SETUP FAIL "binary hash mismatch"; exit 3; fi
guard "write config $CFG"; [ "$DRY" = 1 ] && log "+ write config $CFG" || python3 - "$CFG" <<PY
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
reload
run "$A" check $C || { result SETUP FAIL "seat binding check failed"; exit 3; }
for seat in "$D_NAME:$D_ID" "$U_NAME:$U_ID"; do run "$WAKE" "${seat#*:}" "$(cat "$PLANS/tasks/ack.md")"; done
run systemctl --user start "$U" "$LU.timer"
wait_for "first pass (ok or rest)" 60 state_in ok rest
snap SETUP

# ---------------------------------------------------------------- L1 positive handoff, restart, decide
Q=L1-$RUN; log "L1 onset"
run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task l-worker.md "$Q")" --verify-task "@$(task l-verify.md "$Q")" --duration 10m --verify-window 10m
if wait_for "L1 decision" 600 is_step "$Q" decision; then
  w1=$(wakes "$W_ID"); v1=$(wakes "$V_ID")
  inv=$(prop InvocationID); run systemctl --user restart "$U"; wait_for "L1 restart pass" 90 new_invocation "$inv"
  run "$A" decide $C --qid "$Q" --kind question_answered --ref "P12-live-$RUN-L1" --reason "live witness"
  if is_step "$Q" closed && [ "$(wakes "$W_ID")" = "$w1" ] && [ "$(wakes "$V_ID")" = "$v1" ]; then result L1 PASS "closed; one dispatch per seat across restart"
  else result L1 FAIL "step $(step "$Q"); worker wakes $w1->$(wakes "$W_ID"), verifier $v1->$(wakes "$V_ID")"; fi
else result L1 INCOMPLETE "no verdict within 600 s (step $(step "$Q"))"; fi
snap L1
wait_for "L1 settled" 120 state_is rest
quiet_window L5-rest rest

# ---------------------------------------------------------------- L2 kill during work
Q=L2-$RUN; run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task l-noclaim-worker.md "$Q")" --verify-task "@$(task l-verify.md "$Q")" --duration 3m --verify-window 5m
wait_for "L2 worker step" 30 is_step "$Q" worker
w1=$(wakes "$W_ID"); r1=$(prop NRestarts); inv=$(prop InvocationID)
log "L2 onset: SIGKILL"; run systemctl --user kill -s KILL "$U"
if wait_for "L2 restarted" 30 new_invocation "$inv" && wait_for "L2 pass" 60 state_is ok; then
  if [ "$(prop NRestarts)" -gt "$r1" ] && [ "$(wakes "$W_ID")" = "$w1" ] && journalctl --user -u "$U" --since "-3min" -o cat --no-pager | grep -q held-awaiting-receipt; then
    result L2 PASS "restarted by systemd, outbox held, no resend"
  else result L2 FAIL "restarts $r1->$(prop NRestarts), worker wakes $w1->$(wakes "$W_ID")"; fi
else result L2 FAIL "no restart/pass within bounds"; fi
snap L2
# F3: L2 settles through its own deadline timer: interrupted -> step timed-out (not open), one
# /cancel to the worker, one director wake. decide is not valid here (the core refuses it before a
# verdict: evidence/f3-go-settlement.txt). Later cases start only after this is reconciled.
w2=$(wakes "$W_ID"); d2=$(wakes "$D_ID")
if wait_for "L2 settled by its deadline" 240 is_step "$Q" timed-out; then
  run sleep 10   # the callback's wakes are sent before the step is written; let the send log settle
  if [ "$DRY" = 1 ] || { [ "$(wakes "$W_ID")" -eq $(( w2 + 1 )) ] && [ "$(wakes "$D_ID")" -eq $(( d2 + 1 )) ]; }; then
    result L2-settle PASS "timed-out by its deadline: one /cancel, one director wake; no open work"
  else result L2-settle FAIL "worker wakes $w2->$(wakes "$W_ID"), director $d2->$(wakes "$D_ID")"; fi
else result L2-settle FAIL "L2 not settled (step $(step "$Q"))"; fi
wait_for "L2 rest (no open work)" 120 state_is rest

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
reload; inv=$(prop InvocationID); log "L7c onset: restart with 40 s delay"; run systemctl --user restart --no-block "$U"
wait_for "L7c new invocation" 20 sh -c "[ \"\$(systemctl --user show $U -p InvocationID --value)\" != '$inv' ]"
run systemctl --user start "$LU.service"   # an outside check inside the window
if state_is starting; then s1=PASS; else s1="FAIL($(verdict))"; fi
wait_for "L7c first pass of the new run" 90 state_is ok; run systemctl --user start "$LU.service"
if [ "$s1" = PASS ] && state_is ok; then result L7c PASS "starting (quiet, not recovered) inside the window; ok after the new run's pass"; else result L7c FAIL "window $s1, after $(verdict)"; fi
run rm -f "$SD/$U.d/delay.conf"; reload; snap L7c

# ---------------------------------------------------------------- L3b hang seen by the outside check (watchdog off)
run sh -c "printf '[Service]\nWatchdogSec=0\n' > '$SD/$U.d/nowatchdog.conf'"; reload; run systemctl --user restart "$U"
wait_for "L3b pass" 90 state_is ok
d1=$(wakes "$U_ID"); log "L3b onset: SIGSTOP main pid, no watchdog"; run kill -STOP "$(prop MainPID)"; t0=$(date +%s)
if wait_for "L3b hung" 180 state_is hung; then
  el=$(( $(date +%s) - t0 )); [ "$(wakes "$U_ID")" -gt "$d1" ] && result L3b PASS "hung after ${el}s (bound 180), duty woken" || result L3b FAIL "hung but duty not woken"
else result L3b FAIL "not hung within 180 s"; fi
run kill -CONT "$(prop MainPID)"; run rm -f "$SD/$U.d/nowatchdog.conf"; reload; run systemctl --user restart "$U"
wait_for "L3b recovered" 150 state_is ok; snap L3b

# ---------------------------------------------------------------- L4a restart loop, owned escalation with duty's ack
run sh -c "printf '[Service]\nExecStart=\nExecStart=$A run --config /nonexistent-$RUN.json\n' > '$SD/$U.d/fail.conf'"; reload
log "L4a onset: failing start"; run systemctl --user restart "$U"
[ "$DRY" = 1 ] || systemctl --user show "$U" -p DropInPaths --value | grep -q fail.conf || result L4a INCOMPLETE "fail.conf drop-in not in effect: no onset"
if wait_for "L4a start limit" 120 sh -c "systemctl --user show $U -p Result --value | grep -q start-limit-hit" && wait_for "L4a restart-loop verdict" 60 state_is restart-loop; then
  if wait_for "L4a duty ack recorded" 300 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));a=d[\"open\"][\"ack\"];assert a[\"by\"]==\"$U_NAME\" and a[\"next_action\"] and a[\"response_deadline\"]'"; then
    run rm -f "$SD/$U.d/fail.conf"; reload; run systemctl --user reset-failed "$U"; run systemctl --user start "$U"
    wait_for "L4a recovered" 150 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));assert d.get(\"open\") is None and d[\"history\"][-1][\"outcome\"]==\"recovered\"'" \
      && result L4a PASS "restart-loop -> duty ack (owner/next/deadline) -> recovered on fresh pass" || result L4a FAIL "no recovery after ack"
  else result L4a FAIL "duty never acknowledged"; fi
else result L4a FAIL "no start-limit/restart-loop within bounds"; fi
run rm -f "$SD/$U.d/fail.conf"; reload; run systemctl --user reset-failed "$U"; run systemctl --user start "$U"
wait_for "L4a settled" 90 state_is rest; snap L4a

# ---------------------------------------------------------------- L7a damaged state, L7b future pass (real checker path)
run sh -c "printf '{bad-$RUN' > '$ROOT/$P.db.liveness.json'"; u1=$(wakes "$U_ID")
wait_for "L7a alarm" 60 sh -c "ls $ROOT/$P.db.liveness.json.damaged-*.json"
since=@$(date +%s); run sleep 140
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
# R4: the authorized deadline, from the ledger, before the fault; the send log's size, to read L6's wakes later.
l6dl=$( [ "$DRY" = 1 ] && echo DRY || $A status $C --json 2>>"$EV/driver.log" | python3 -c "import json,sys; print([p['deadline'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0])" 2>>"$EV/driver.log" )
nl0=$( [ "$DRY" = 1 ] && echo 0 || wc -l < /home/bmosher/.local/share/agent-deck/wake-send.log )
c1=$(wakes "$W_ID"); dd1=$(wakes "$D_ID"); tstop=@$(date +%s)
log "L5 onset: agent-loop stop"; run "$A" stop $C
wait_for "L5 run exited" 60 sh -c "systemctl --user show $U -p ExecMainStatus --value | grep -qx 64"
st=$(prop ActiveState)
log "L5: stray start while the marker exists"; run systemctl --user start "$U"; src=$?
run sleep 20   # longer than RestartSec: a restart storm would show by now
sched=$( [ "$DRY" = 1 ] && echo 0 || journalctl --user -u "$U" --since "$tstop" -o cat --no-pager | grep -c "Scheduled restart" )
[ "$sched" -eq 0 ] && [ -e "$ROOT/$P.db.stop" ] && [ "$(prop ActiveState)" != active ] \
  && result L5-stray PASS "exit 64 (state $st); stray start rc=$src (recorded, not assumed 0); marker kept; no scheduled restart" \
  || result L5-stray FAIL "scheduled restarts $sched, state $(prop ActiveState), marker $(ls "$ROOT/$P.db.stop" 2>&1)"
quiet_window L5-stopped stopped 245    # R3: 245 s collection; the L6 deadline (2 min) falls inside it
l6_timing
if [ "$DRY" = 1 ] || { [ "$(wakes "$W_ID")" -eq $(( c1 + 1 )) ] && [ "$(wakes "$D_ID")" -eq $(( dd1 + 1 )) ] && journalctl --user -u "agent-loop-$P-$Q-w1.service" -o cat --no-pager | grep -q interrupted; }; then
  run systemctl --user start "agent-loop-$P-$Q-w1.service"   # replay the callback
  if [ "$DRY" = 1 ] || { [ "$(wakes "$W_ID")" -eq $(( c1 + 1 )) ] && journalctl --user -u "agent-loop-$P-$Q-w1.service" -o cat --no-pager | tail -n 3 | grep -q already-handled; }; then
    result L6 PASS "interrupted once while run was stopped: one /cancel, one director wake; replay already-handled"
  else result L6 FAIL "replay repeated effects"; fi
else result L6 FAIL "cancel/director wakes $c1->$(wakes "$W_ID") $dd1->$(wakes "$D_ID")"; fi
run "$A" start $C; wait_for "L5 resumed" 90 sh -c "systemctl --user is-active $U"; snap L5-L6

# ---------------------------------------------------------------- L4b duty unavailable (last: it stops the duty seat)
if ! stop_seat "$U_ID"; then
  result L4b INCOMPLETE "duty fixture $U_ID not confirmed stopped (registry: $(seat_status "$U_ID")): no onset injected"
else
run sh -c "printf '[Service]\nExecStart=\nExecStart=$A run --config /nonexistent-$RUN.json\n' > '$SD/$U.d/fail.conf'"; reload
d1=$(wakes "$D_ID"); log "L4b onset: failing start, duty seat $U_ID confirmed stopped"; run systemctl --user restart "$U"
if wait_for "L4b restart-loop" 180 state_is restart-loop && [ "$DRY" = 1 -o "$(wakes "$D_ID")" -gt "$d1" ]; then
  wait_for "L4b director ack" 300 sh -c "python3 -c 'import json;d=json.load(open(\"$ROOT/$P.db.liveness.json\"));assert d[\"open\"][\"ack\"][\"by\"]==\"$D_NAME\"'" \
    && result L4b PASS "duty wake failed -> director woken in the same check -> director ack recorded" || result L4b FAIL "no director ack"
else result L4b FAIL "observed $(verdict | cut -d' ' -f1) (required restart-loop); director wakes $d1 -> $(wakes "$D_ID")"; fi
run rm -f "$SD/$U.d/fail.conf"; reload
fi
snap L4b

log "all cases run; results in $EV/results.tsv"
if grep -qP '\t(FAIL|INCOMPLETE)\t' "$EV/results.tsv"; then log "NOT ALL PASS: $(grep -cP '\t(FAIL|INCOMPLETE)\t' "$EV/results.tsv") FAIL/INCOMPLETE rows"; exit 1; fi
# cleanup runs from the trap
