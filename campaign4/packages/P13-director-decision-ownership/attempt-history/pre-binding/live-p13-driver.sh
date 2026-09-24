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
PKG=/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
PLANS=$PKG/plans
# shellcheck disable=SC1090
. "$INPUTS"
for v in RUN ROOT LIVE_DEADLINE PROFILE WAKE WAKE_SHA PASSIVE_LANE PASSIVE_LANE_SHA PASSIVE_ENGINE PASSIVE_ENGINE_SHA STREAMS BIN_SRC BIN_SHA UNITS_SRC W_NAME W_ID V_NAME V_ID D_NAME D_ID U_NAME U_ID NOTIFY_CLAUDE_SRC NOTIFY_CLAUDE_SHA ESCALATIONS_SRC ESCALATIONS_SHA ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
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
LF=agent-loop-liveness-failed-$P   # P12-checker-ownership-1: the check's OnFailure handler
SD=/home/bmosher/.config/systemd/user
# P13 live composition: INJECT=1 is the OS/transport-injection TEST of this exact branch (stubs on PATH,
# private unit dir). It is labelled on every row and can never count as live. Live refuses any stub.
INJECT=${INJECT:-0}
if [ "$INJECT" = 1 ]; then SD=${INJECT_SD:?INJECT_SD required}; else
  for t in systemctl systemd-run agent-deck journalctl; do case "$(command -v $t)" in /usr/bin/*|/home/bmosher/.local/bin/*|/var/home/bmosher/.local/bin/*) ;; *) echo "live: $t resolves to '$(command -v $t)', not an installed tool (stub?)" >&2; exit 2;; esac; done
  [ -z "${EV_DIR:-}" ] || { echo "live: EV_DIR (offline evidence override) is forbidden" >&2; exit 2; }
fi
[ "$(sha256sum "$WAKE" | cut -d' ' -f1)" = "$WAKE_SHA" ] || { echo "WAKE is not the pinned real wake ($WAKE)" >&2; exit 2; }
case "$WAKE" in */fixture-wake.sh|*stub*) echo "WAKE must be the real agent-deck wake, not a fixture" >&2; exit 2;; esac
EV=${EV_DIR:-$PKG/live-$RUN}   # EV_DIR only for offline rehearsal
WALL=p13live-wallstop-$RUN
SCOPE=p13live-driver-$RUN   # F2: the driver and every child run in this owned scope
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
result() { local st=$2; [ "$DRY" = 1 ] && st=DRY; [ "$INJECT" = 1 ] && st="INJECTED-$st"; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/results.tsv"; }
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
wakes() { if [ "$DRY" = 1 ]; then echo 0; return; fi; grep -c "$1" $HOME/.local/share/agent-deck/wake-send.log; }
snap() { # case label: everything a reviewer needs, before and after
  { echo "## $1 $(ts)"; show; state; $A expose $C --json; tail -n 20 $HOME/.local/share/agent-deck/wake-send.log;
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
# P13-live-measurement-1: evaluations live in live-checks.sh (pure; tested on the saved live1 raws). Journal
# reads are captured whole (never `| grep -q` under pipefail: SIGPIPE 141 hid live1 L3a's watchdog line).
. "$PKG/../P12-timeout-ownership-live-closure/plans/live-checks.sh"   # pinned P12 evaluators (read-only)
jcap() { journalctl --user -u "$1" --since "@$2" -o short-unix --no-pager 2>>"$EV/driver.log"; }
# healthy_after EPOCH: verdict ok|rest checked after EPOCH AND the ledger's own pass record (read-only) is from
# at/after EPOCH by the unit's CURRENT invocation and main pid. Fail-closed on any missing/malformed input.
loop_pass() { python3 -c 'import sqlite3,sys; c=sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True, timeout=1); print(c.execute("select value from driver_kv where key=?", ("loop-pass",)).fetchone()[0])' "$ROOT/$P.db" 2>>"$EV/driver.log"; }
healthy_after() { local v; v=$(verdict) || return 1; healthy_eval "$1" "$v" || return 1; loop_pass | pass_eval "$1" "$(prop InvocationID)" "$(prop MainPID)"; }
stop_exited() { local r; r=$(journalctl --user -u "$U" --since "@$1" -o cat --no-pager 2>>"$EV/driver.log" | stop_exit_eval); [ "${r%% *}" = PASS ] && [ "$(prop ActiveState)" != active ]; }
restart_loop_proven() { local r; r=$(jcap "$U" "$1" | start_limit_eval "$1" "$U" "$(systemctl --user show "$U" -p StartLimitBurst --value)"); log "restart-loop evidence: $r"; [ "${r%% *}" = PASS ]; }
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
# acknowledgement's host time (status timeout.ack.at, by the director or duty): at most 60 s after
# detection AND at most 90 s after the deadline, in order deadline <= detection <= ack (P12-review-1:
# a total-only bound let detection 10 s + ack 90 s through). A sent wake is never ownership. Timer lateness counts against detection; it is never
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
own = (ak - dl).total_seconds(); gap = (ak - it).total_seconds()
ok = 0 <= det <= 30 and 0 <= gap <= 60 and own <= 90
print("%s explicit: detection %.1fs (bound 30), ack %.1fs after detection (bound 60), %.1fs after deadline (bound 90), deadline %s" % ("PASS" if ok else "FAIL", det, gap, own, sys.argv[1]))' "$@"; }
l6_timing() {
  if [ "$DRY" = 1 ]; then result L6-timing DRY "deadline/settled/ack timestamps"; return; fi
  local tj r
  wait_for "L6 acknowledged" 120 sh -c "$A status $C --json | python3 -c \"import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert (p.get('timeout') or {}).get('ack')\""
  tj=$($A status $C --json 2>>"$EV/driver.log" | python3 -c "import json,sys; print(json.dumps([p.get('timeout') or {} for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]))" 2>>"$EV/driver.log")
  printf '{"deadline": "%s", "callback_start": "%s", "timeout": %s}\n' "$l6dl" "$(systemctl --user show "agent-loop-$P-$Q-w1.service" -p ExecMainStartTimestamp --value 2>&1)" "${tj:-null}" > "$EV/l6-timing.json"
  local st ak
  # P12-ack-capacity-1: detection is the EARLIEST trusted time (the due marker, deferred_callback, when the
  # callback had to leave one; else the settlement "at"); the 60 s ack bound runs from it and never moves.
  st=$(printf '%s' "$tj" | python3 -c 'import json,sys
try:
    t = json.load(sys.stdin); print(min(x for x in (t.get("at"), t.get("deferred_callback")) if x))
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
  if [ "$DRY" != 1 ]; then
    [ -d "$ROOT/$P.db.caps" ] && find "$ROOT/$P.db.caps" -printf "%m %p\n" > "$EV/archive/caps-redacted.txt"   # modes/paths only
    ( cd "$ROOT" && tar --exclude="./$P.db.caps" -cf - . ) | ( cd "$EV/archive" && tar -xf - ) 2>>"$EV/driver.log"
    run rm -rf "$ROOT/$P.db.caps"
  fi
  run systemctl --user stop "$LU.timer" "$LU.service" "$LF.service" "$U"
  for t in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do run systemctl --user stop "$t"; done
  run systemctl --user reset-failed "agent-loop-$P*" "$LU*" "$LF*"
  run rm -f "$SD/$U" "$SD/$LU.service" "$SD/$LU.timer" "$SD/$LF.service"
  run rm -rf "$SD/$U.d"
  run systemctl --user daemon-reload
  for id in $W_ID $V_ID $D_ID $U_ID; do run agent-deck session stop "$id"; run agent-deck session remove "$id"; done
  run systemctl --user stop "$WALL.timer"
  # R2: outcomes are checked, not assumed: every fixture gone from the registry, no unit of this run active.
  local left="" id u
  if [ "$DRY" != 1 ]; then
    for id in $W_ID $V_ID $D_ID $U_ID; do st=$(seat_status "$id"); [ "$st" = absent ] || left="$left seat $id ($st);"; done
    for u in "$LU.timer" "$LU.service" "$LF.service" "$U" $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do
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
# L6b (no ack while run is stopped): timeout JSON on stdin -> "PASS|FAIL detail". Bounds from
# settlement (checker = calendar timer every 30 s, AccuracySec=1s, P12-bounded-deadline-1): duty
# 60..95 s (60 + 30 + 1 + check time), director 120..155 s, and no acknowledgement recorded.
l6b_eval() { python3 -c '
import json, sys, datetime as D
try:
    t = json.load(sys.stdin)
    def at(s): return D.datetime.fromisoformat(s.split()[-1].replace("Z", "+00:00"))
    st = at(t["at"]); du = (at(t["no_ack_duty"]) - st).total_seconds(); di = (at(t["no_ack_director"]) - st).total_seconds()
except Exception as e:
    print("FAIL unreadable timeout record:", e); sys.exit()
ok = 60 <= du <= 95 and 120 <= di <= 155 and not t.get("ack")
print("%s duty %.0fs after settlement (60..95), director %.0fs (120..155), ack %s" % ("PASS" if ok else "FAIL", du, di, t.get("ack")))'; }
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
if [ "$DRY" != 1 ] && [ "${P13_IN_SCOPE:-}" != "$SCOPE" ]; then
  [ "$(_now)" -lt "$DL_EPOCH" ] || { result SETUP INCOMPLETE "live deadline $LIVE_DEADLINE already passed: no effect started"; exit 3; }
  # Not exec: if systemd-run cannot create the scope, say so instead of ending silently.
  env P13_IN_SCOPE="$SCOPE" systemd-run --user --scope --quiet --unit="$SCOPE" -- /bin/bash "$0" "$@"; rc=$?
  [ -e "$EV/scope-entered.$SCOPE" ] || { result SETUP FAIL "owned scope $SCOPE not created (systemd-run rc=$rc): no effect started"; exit 3; }
  exit $rc
fi
if [ "$DRY" != 1 ] && [ "$INJECT" != 1 ] && ! grep -q "/$SCOPE.scope\$" /proc/$$/cgroup; then result SETUP FAIL "driver is not in $SCOPE.scope"; exit 3; fi
[ "$DRY" = 1 ] || touch "$EV/scope-entered.$SCOPE"
# A stop of the scope (the wall) must not start a second cleanup from inside it.
trap 'trap - EXIT; log "driver terminated by signal (wall stop)"; exit 143' TERM

# ---------------------------------------------------------------- setup
log "P13 live $RUN, inputs sha256 $(sha256sum "$INPUTS" | cut -d' ' -f1)"
now=$(date +%s); dl=$(date -d "$LIVE_DEADLINE" +%s)
if [ "$dl" -le "$now" ]; then log "live deadline $LIVE_DEADLINE already passed"; result SETUP INCOMPLETE "deadline passed"; exit 3; fi
# Bounded wall stop, armed before any task: cleanup runs at the live deadline even if this shell dies.
run systemd-run --user --unit="$WALL" --timer-property=AccuracySec=1s --on-calendar="$(date -u -d @$DL_EPOCH '+%Y-%m-%d %H:%M:%S') UTC" --setenv=PATH="$PATH" --setenv=AGENTDECK_PROFILE="$PROFILE" ${EV_DIR:+--setenv=EV_DIR="$EV_DIR"} /bin/bash "$PLANS/live-p13-driver.sh" "$INPUTS" cleanup \
  || { result SETUP FAIL "wall-stop not armed: no effect started"; exit 3; }
if [ "$DRY" != 1 ] && { [ "$(systemctl --user is-active "$WALL.timer")" != active ] || ! wall_ok; }; then result SETUP FAIL "wall-stop timer $WALL.timer not active at $LIVE_DEADLINE ($(wall_next)): no effect started"; exit 3; fi
trap cleanup EXIT   # armed and verified: from here every exit cleans up exact IDs once
if [ -e "$ROOT" ] && [ "$DRY" != 1 ]; then result SETUP INCOMPLETE "private root $ROOT exists"; exit 3; fi
run mkdir -p "$ROOT/bin" "$ROOT/art" "$ROOT/claims" "$ROOT/tasks" "$ROOT/home/.config/agent-deck" "$ROOT/home/.local/share/agent-deck"
# Private HOME: the PINNED real notify-claude and escalations (private ledger; real labelled chat notice),
# the private candidate watcher/resolver, and a stub pager (never Signal).
for pair in "$NOTIFY_CLAUDE_SRC:$NOTIFY_CLAUDE_SHA:notify-claude" "$ESCALATIONS_SRC:$ESCALATIONS_SHA:escalations" "$ADAPTER_WATCH_SRC:$ADAPTER_WATCH_SHA:escalation-watch" "$ADAPTER_RESOLVE_SRC:$ADAPTER_RESOLVE_SHA:escalation-resolve"; do
  IFS=: read -r src sha name <<<"$pair"
  run install -m 755 "$src" "$ROOT/home/.config/agent-deck/$name"
  [ "$(sha256sum "$ROOT/home/.config/agent-deck/$name" | cut -d' ' -f1)" = "$sha" ] || { result SETUP FAIL "$name hash mismatch"; exit 3; }
done
run install -m 755 "$PLANS/ticket-page-stub.sh" "$ROOT/home/.config/agent-deck/ticket"
run install -m 755 "$BIN_SRC" "$A"
if [ "$DRY" != 1 ] && [ "$(sha256sum "$A" | cut -d' ' -f1)" != "$BIN_SHA" ]; then result SETUP FAIL "binary hash mismatch"; exit 3; fi
guard "write config $CFG"; [ "$DRY" = 1 ] && log "+ write config $CFG" || python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "$P", "profile": "$PROFILE", "wake": "$WAKE", "db": "$ROOT/$P.db", "stream_dir": "$STREAMS",
  "claims_dir": "$ROOT/claims", "artifacts_dir": "$ROOT/art", "director": "$D_NAME", "duty": "$U_NAME",
  "seats": {"$W_NAME": "$W_ID", "$V_NAME": "$V_ID", "$D_NAME": "$D_ID", "$U_NAME": "$U_ID"},
  "bin": "$A", "unit": "$U",
  "decision_deadline_s": 60, "decision_policy": "",
  "decision_ladder": [{"after_s": 0, "seat": "$D_NAME"}, {"after_s": 20, "seat": "$U_NAME"},
    {"after_s": 40, "exec": ["/usr/bin/env", "HOME=$ROOT/home", "$ROOT/home/.config/agent-deck/notify-claude", "decision"],
     "ledger": "$ROOT/home/.local/share/agent-deck/escalations.jsonl", "ledger_kind": "decision",
     "resolve_cmd": ["/usr/bin/env", "HOME=$ROOT/home", "$ROOT/home/.config/agent-deck/escalation-resolve"]}],
  "decision_responders": ["claude"]}, open(sys.argv[1], "w"), indent=1)
PY
sub="s#agent-loop-liveness-failed@%i.service#$LF.service#g; s#agent-loop-liveness@%i.service#$LU.service#g; s#%h/.local/bin/agent-loop#$A#g; s#%h/.config/agent-loop/%i.json#$CFG#g; s#agent-loop %i#agent-loop $P#g; s#%i#$P#g"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop@.service' > '$SD/$U'"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop-liveness@.service' > '$SD/$LU.service'"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop-liveness@.timer' > '$SD/$LU.timer'"
run sh -c "sed '$sub' '$UNITS_SRC/agent-loop-liveness-failed@.service' > '$SD/$LF.service'"
run grep -c "$A" "$SD/$U" "$SD/$LU.service" "$SD/$LF.service"
run grep -q "^OnFailure=$LF.service$" "$SD/$LU.service" || { result SETUP FAIL "check unit has no OnFailure=$LF.service"; exit 3; }
reload
run "$A" check $C || { result SETUP FAIL "seat binding check failed"; exit 3; }
run systemctl --user start "$U" "$LU.timer"
wait_for "first pass (ok or rest)" 60 state_in ok rest
snap SETUP

# ---------------------------------------------------------------- P13 decision ownership (live sequence)
# Real worker/verifier: tasks run the candidate claim CLI and end their turn; the runtime writes the stream.
Q=D$RUN
st() { "$A" status $C --json | python3 -c "import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; d=p.get('decision') or {}; print(eval(sys.argv[1]))" "$1"; }
# INDUCTION (P13-passive-fixture-1): director and duty are PASSIVE RECEIVERS (plans/acp-passive-lane: the real
# acp-worker runtime + plans/passive-acp-engine.py, which has no tools and cannot execute any notice text).
# Before dispatch: the pinned lane/engine bytes must match, and a probe with a fresh nonce sent through the
# REAL wake must appear in each receiver's own record (real receive protocol). Missing receiver, wrong bytes
# or no record -> INDUCTION INVALID (exit 4), no dispatch. The driver alone acknowledges and decides later.
for pair in "$PASSIVE_LANE:$PASSIVE_LANE_SHA" "$PASSIVE_ENGINE:$PASSIVE_ENGINE_SHA"; do
  [ "$(sha256sum "${pair%%:*}" 2>/dev/null | cut -d' ' -f1)" = "${pair#*:}" ] || { result INDUCTION INVALID "passive fixture bytes differ: ${pair%%:*}"; exit 4; }
done
for sid in "$D_ID" "$U_ID"; do
  n=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n'); echo "$n" > "$ROOT/probe-$sid.nonce"
  guard "probe $sid"; log "+ $WAKE $sid <passive-receiver probe for run $RUN>"
  "$WAKE" "$sid" "P13 passive receiver probe, run $RUN, seat $sid, nonce $n" >>"$EV/driver.log" 2>&1; rc=$?
  [ $rc = 0 ] || [ $rc = 3 ] || { result INDUCTION INVALID "probe not delivered to $sid (wake rc $rc): receiver missing"; exit 4; }
done
received() { for sid in "$D_ID" "$U_ID"; do grep -q "nonce $(cat "$ROOT/probe-$sid.nonce")" "$HOME/.local/share/p13-passive/$sid.jsonl" 2>/dev/null || return 1; done; }
wait_for "both passive receivers recorded their probe" 60 received || { result INDUCTION INVALID "a passive receiver did not record its probe (director/duty not passive or not running)"; exit 4; }
result INDUCTION PASS "director and duty are passive receivers (pinned bytes, probe recorded through the real wake)"
premature() { [ -n "$(st "d.get('resolved','')")" ] && { result PRECONDITION INVALID "incident resolved at $(st "d.get('resolved','')") before the plan's decide ($1): the ladder test is invalid, not a product result"; exit 4; }; return 0; }
run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task decision-worker-live.md "$Q")" --verify-task "@$(task decision-verify-live.md "$Q")" --duration 8m --verify-window 8m \
  || { result DISPATCH FAIL "dispatch refused"; exit 3; }
wait_for "decision step (real worker + verifier claims)" 600 sh -c "s=\$('$A' expose $C --json 2>/dev/null | python3 -c \"import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0])\"); [ \"\$s\" = decision ] || [ \"\$s\" = closed ]" || { result DECISION FAIL "package never reached decision (step $(step "$Q"))"; exit 3; }
premature "at decision entry"
[ -n "$(st "d.get('deadline','')")" ] && systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" | grep -q -- "-decision" \
  || { result DECISION FAIL "no persisted deadline or no decision timer unit"; exit 3; }
INC=$(st "d['incident']"); result DECISION PASS "incident $INC, deadline $(st "d['deadline']")"
w0d=$(wakes "$D_ID"); w0u=$(wakes "$U_ID")
t_stop=$(date +%s); run "$A" stop $C
wait_for "run exited 64 on the stop marker" 60 stop_exited "$t_stop" || { result STOP FAIL "run did not stop on the marker"; exit 3; }
premature "after stop"
result STOP PASS "intentional stop marker after the authentic decision; timer + outside check own the ladder"
E=$ROOT/home/.local/share/agent-deck/escalations.jsonl
DL=$(st "d['deadline']"); DLE=$(date -u -d "$DL" +%s)
. "$PLANS/rung-eval.sh"
rung_ok() { premature "rung $1"; rung_eval "$(st "d.get('rungs') and d['rungs'].get('$1','') or ''")" "$HOME/.local/share/agent-deck/wake-send.log" "$2" "$INC" "$DLE"; }
wait_for "director rung 0 (DB + transport, incident-bound)" 150 rung_ok 0 "$D_ID" || { result RUNGS FAIL "rung 0: DB '$(st "d.get('rungs',{}).get('0','')")', no incident-bound director transport after $DL"; exit 3; }
wait_for "duty rung 1 (DB + transport, incident-bound)" 90 rung_ok 1 "$U_ID" || { result RUNGS FAIL "rung 1: DB '$(st "d.get('rungs',{}).get('1','')")', no incident-bound duty transport"; exit 3; }
wait_for "Claude rung 2 (DB + private ledger)" 90 sh -c "grep -q 'DECISION OVERDUE $INC' '$E'" || { result RUNGS FAIL "no private ledger record"; exit 3; }
premature "rung 2"
[ "$(st "d['rungs'].get('2','')" | cut -c1-4)" = sent ] || { result RUNGS FAIL "Claude rung not recorded sent"; exit 3; }
result RUNGS PASS "director, duty (real wakes), Claude (private ledger + real labelled notify-claude) while stopped"
ACKF="$ROOT/$P.db.caps/$INC.claude"
[ "$(stat -c %a "$ACKF" 2>/dev/null)" = 600 ] || { result ACK FAIL "no 0600 capability file"; exit 3; }
"$A" decision-ack $C --qid "$Q" --by claude --next x --within 60s >>"$EV/driver.log" 2>&1 && { result ACK FAIL "literal ack accepted"; exit 3; }
premature "before ack"
run "$A" decision-ack $C --qid "$Q" --by claude --cap-file "$ACKF" --next "fixture: chase the director" --within 60s || { result ACK FAIL "capability ack refused"; exit 3; }
result ACK PASS "literal refused; capability ack recorded (60 s)"
wait_for "expiry re-raise" 150 sh -c "\"$A\" status $C --json | python3 -c \"import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert (p.get('decision') or {}).get('reraised','').startswith('sent')\"" || { result RECUR FAIL "no re-raise"; exit 3; }
KEYS=$(python3 -c "import json; print(' '.join(r['key'] for r in map(json.loads, filter(str.strip, open('$E'))) if 'id' in r and '$INC' in r.get('text','')))")
set -- $KEYS; [ $# -eq 2 ] && [ "$1" = "$2" ] || { result RECUR FAIL "want 2 records, one key: $KEYS"; exit 3; }
KEY1=$1; result RECUR PASS "same key $KEY1"
premature "before the plan decide"
run "$A" decide $C --qid "$Q" --kind question_answered --ref "P13-live-$RUN" --reason "fixture decision"
[ -n "$(st "d.get('resolved','')")" ] && grep -q "\"resolve\": \"$KEY1\"" "$E" || { result DECIDE FAIL "not resolved / no resolution record"; exit 3; }
HOME="$ROOT/home" ESCALATION_GRACE_MIN=0 FIXTURE_TICKET_LOG="$ROOT/ticket" python3 "$ROOT/home/.config/agent-deck/escalation-watch" >>"$EV/driver.log" 2>&1
grep -q "$INC" "$ROOT/ticket.pages" 2>/dev/null && { result DECIDE FAIL "resolved incident paged"; exit 3; }
result DECIDE PASS "resolved; private watcher quiet"
t_start=$(date +%s); run "$A" start $C
wait_for "restart: fresh pass" 90 healthy_after "$t_start" || { result RESTART FAIL "no fresh pass after start"; exit 3; }
nd=$(( $(wakes "$D_ID") - w0d )); nu=$(( $(wakes "$U_ID") - w0u )); nl=$(grep -c "DECISION OVERDUE $INC" "$E")
[ "$nd" = 1 ] && [ "$nu" = 1 ] && [ "$nl" = 2 ] || { result RESTART FAIL "director $nd, duty $nu (want 1 each), ledger $nl (want 2)"; exit 3; }
result LIVE PASS "authentic decision, stop marker, ladder, capability ack/expiry/same-key recurrence, decide + quiet watcher, restart without duplicates"
log "all cases run; results in $EV/results.tsv"
if grep -qP '\t(INJECTED-)?(FAIL|INCOMPLETE|INVALID)\t' "$EV/results.tsv"; then log "NOT ALL PASS"; exit 1; fi
