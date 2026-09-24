#!/bin/bash
# P13 live20 decision-ownership plan, REPAIRED (F1-F4). Preserved v1 archive:
# evidence/plan-repair/v1/. Runs ONLY after Tern signs the filled INPUTS hash.
# Offline proof: evidence/plan-repair/offline-test.sh runs this file's exact
# top-level run path under dependency-injected stubs + the REAL candidate
# binary on throwaway ledgers (no DRY=1 as behavioral evidence).
#
# Private ROOT isolates every effect. No live fixture launches, service
# changes, wakes/Signal, or shared ledger writes in offline tests.
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
PLANS=$PKG/plans
# shellcheck disable=SC1090
. "$INPUTS"
for v in RUN ROOT LIVE_DEADLINE PROFILE WAKE STREAMS BIN_SRC BIN_SHA UNITS_SRC W_NAME W_ID V_NAME V_ID D_NAME D_ID U_NAME U_ID RUNG0_S RUNG1_S RUNG2_S DECISION_WINDOW_S ESC_LEDGER NOTIFY_CLAUDE RESOLVE_CMD TICKET_STUB ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
  val=${!v:-}
  if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
# DECISION_POLICY "" (generic fixture) is a valid explicit value, not "unfilled".
case "${DECISION_POLICY-unset}" in ""|required) ;; *) echo "input DECISION_POLICY must be empty (generic) or required" >&2; exit 2;; esac
for id in $W_ID $V_ID $D_ID $U_ID; do
  case " 0c933c75-1790000758 493c0317-1790000758 a79067ca-1790000758 56513e0e-1790000758 " in *" $id "*) echo "main seat $id is forbidden" >&2; exit 2;; esac
done
[ "$(printf '%s\n' "$W_ID" "$V_ID" "$D_ID" "$U_ID" | sort -u | wc -l)" -eq 4 ] || { echo "fixture IDs must be four distinct values" >&2; exit 2; }
DL_EPOCH=$(date -u -d "$LIVE_DEADLINE" +%s 2>/dev/null) || { echo "LIVE_DEADLINE invalid" >&2; exit 2; }
# F2: no exported private HOME. Caller HOME/PATH are inherited untouched;
# escalation isolation uses absolute private paths per command instead.
P=p13d$RUN
A=$ROOT/bin/agent-loop
CFG=$ROOT/$P.json
C="--config $CFG"
U=agent-loop-$P.service
LU=agent-loop-liveness-$P
LF=agent-loop-liveness-failed-$P
SD=$ROOT/systemd/user
EV=${EV_DIR:-$PKG/evidence/plan-repair/$RUN}
WALL=p13live-wallstop-$RUN
SCOPE=p13live-driver-$RUN
mkdir -p "$EV"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/driver.log"; }
_now() { date +%s; }
guard() { [ -n "${TEARDOWN:-}" ] || [ "$(_now)" -lt "$DL_EPOCH" ] && return 0
  echo "$(ts) DEADLINE: refused: $*" >>"$EV/driver.log"
  result DEADLINE INCOMPLETE "refused at $(ts): $*"; exit 3; }
run() { guard "$@"; log "+ $*"; "$@" >>"$EV/driver.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
out() { echo "$(ts) + $* (captured)" >>"$EV/driver.log"; "$@" 2>>"$EV/driver.log"; }
result() { local st=$2; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/results.tsv"; }
. "$PLANS/decision-evaluators.sh"
wait_for() { local label=$1 limit=$2; shift 2; local t0; t0=$(date +%s)
  while ! "$@" >/dev/null 2>&1; do
    if [ $(( $(date +%s) - t0 )) -ge "$limit" ]; then log "timeout waiting for $label"; result "wait:$label" INCOMPLETE "not reached in ${limit}s"; return 1; fi; sleep 2; done
  log "reached $label after $(( $(date +%s) - t0 ))s"; }
cleanup() {
  trap - EXIT; TEARDOWN=1
  if ! mkdir "$EV/cleanup.lock" 2>/dev/null; then log "cleanup already ran"; return 0; fi
  log "cleanup (exact IDs)"
  mkdir -p "$EV/archive"
  # F4: NEVER archive secret contents. Caps are listed as redacted
  # hashes/permissions only; the actual db.caps tree is removed below.
  if [ -d "$ROOT/caps" ]; then
    { echo "# caps redaction record (hashes/permissions only, no contents)";
      find "$ROOT/caps" -type f -exec sha256sum {} \; ;
      find "$ROOT/caps" -printf "%m %p\n"; } >"$EV/archive/caps-redacted.txt" 2>/dev/null
  fi
  cp -a "$ROOT"/db* "$ROOT"/escalations.jsonl "$EV/archive/" 2>/dev/null
  # Wall stops the ORIGINAL driver scope/process first (was missing in v1).
  if systemctl --user is-active "$SCOPE.scope" >/dev/null 2>&1; then
    log "WALLSTOP: stopping $SCOPE.scope"; run systemctl --user stop "$SCOPE.scope"
  fi
  run systemctl --user stop "$LU.timer" "$LU.service" "$LF.service" "$U"
  for t in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do run systemctl --user stop "$t"; done
  run systemctl --user reset-failed "agent-loop-$P*" "$LU*"
  run rm -f "$SD/$U" "$SD/$LU.service" "$SD/$LU.timer" "$SD/$LF.service"
  run systemctl --user daemon-reload
  for id in $W_ID $V_ID $D_ID $U_ID; do run agent-deck session stop "$id"; run agent-deck session remove "$id"; done
  run systemctl --user stop "$WALL.timer"
  # F4: remove the ACTUAL db.caps tree for this run (exact scope), after the
  # redacted record above. No unrelated caps touched: path is run-scoped.
  run rm -rf "$ROOT/caps"
  # F4: remaining-seat check uses CAPTURED output, not run() logging.
  local left="" st
  for id in $W_ID $V_ID $D_ID $U_ID; do
    st=$(agent-deck list --json 2>>"$EV/driver.log" | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get("sessions",[]); print(next((r.get("status","") for r in d if r.get("id")==sys.argv[1]),"absent"))' "$id" 2>>"$EV/driver.log") || st="unreadable"
    [ "$st" = absent ] || left="$left seat $id ($st);"
  done
  for u in "$LU.timer" "$LU.service" "$LF.service" "$U" $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do
    [ "$(systemctl --user is-active "$u" 2>/dev/null)" = active ] && left="$left unit $u active;"
  done
  [ -d "$ROOT/caps" ] && left="$left caps dir remains;"
  if [ -n "$left" ]; then result CLEANUP FAIL "unresolved:$left"; return 1; fi
  log "cleanup done"
}
wall_ok() { [ "$(systemctl --user show "$WALL.timer" -p TimersCalendar --timestamp=unix --value 2>/dev/null | grep -o 'next_elapse=@[0-9]*' | cut -d= -f2)" = "@$DL_EPOCH" ]; }
if [ "$MODE" = cleanup ]; then TEARDOWN=1; cleanup; exit 0; fi

# ---------------------------------------------------------------- setup
log "P13 live $RUN, inputs sha256 $(sha256sum "$INPUTS" | cut -d' ' -f1)"
if [ -e "$ROOT" ]; then result SETUP INCOMPLETE "private root exists"; exit 3; fi
run mkdir -p "$ROOT/bin" "$ROOT/home" "$ROOT/art" "$ROOT/claims" "$ROOT/caps" "$ROOT/tasks" "$ROOT/streams"
run install -m 755 "$PLANS/fixture-wake.sh" "$WAKE"
run install -m 755 "$PLANS/ticket-notify.sh" "$NOTIFY_CLAUDE"
export FIXTURE_WAKE_LOG="$ROOT/wake.log" FIXTURE_TICKET_LOG="$TICKET_STUB"
run chmod 700 "$ROOT/caps"
run install -m 755 "$BIN_SRC" "$A"
[ "$(sha256sum "$A" | cut -d' ' -f1)" = "$BIN_SHA" ] || { result SETUP FAIL "binary hash mismatch"; exit 3; }
run mkdir -p "$(dirname "$ESC_LEDGER")" "$(dirname "$NOTIFY_CLAUDE")" "$(dirname "$RESOLVE_CMD")"
run install -m 755 "$ADAPTER_WATCH_SRC" "$ROOT/bin/escalation-watch"
run install -m 755 "$ADAPTER_RESOLVE_SRC" "$ROOT/bin/escalation-resolve"
[ "$(sha256sum "$ROOT/bin/escalation-watch" | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] || { result SETUP FAIL "watch adapter hash mismatch"; exit 3; }
[ "$(sha256sum "$ROOT/bin/escalation-resolve" | cut -d' ' -f1)" = "$ADAPTER_RESOLVE_SHA" ] || { result SETUP FAIL "resolve adapter hash mismatch"; exit 3; }
# F1: FULL live config — every field the candidate run path needs. No stub ticket
# overwrite: NOTIFY_CLAUDE names the real per-run notify path used below.
guard "write fixture config"
python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "$P", "profile": "$PROFILE", "wake": "$WAKE",
 "db": "$ROOT/$P.db", "stream_dir": "$STREAMS",
 "claims_dir": "$ROOT/claims", "artifacts_dir": "$ROOT/art",
 "director": "$D_NAME", "duty": "$U_NAME",
 "seats": {"$W_NAME": "$W_ID", "$V_NAME": "$V_ID", "$D_NAME": "$D_ID", "$U_NAME": "$U_ID"},
 "bin": "$A", "unit": "$U",
 "decision_policy": "$DECISION_POLICY",
 "decision_deadline_s": $DECISION_WINDOW_S,
 "decision_ladder": [{"after_s": $RUNG0_S, "seat": "$D_NAME"}, {"after_s": $RUNG1_S, "seat": "$U_NAME"},
  {"after_s": $RUNG2_S, "exec": ["$NOTIFY_CLAUDE", "decision"], "ledger": "$ESC_LEDGER", "ledger_kind": "decision", "resolve_cmd": ["$ROOT/bin/escalation-resolve"]}],
 "decision_responders": ["claude"]}, open(sys.argv[1], "w"), indent=1)
PY
python3 -c "import json; cfg=json.load(open('$CFG')); assert cfg['decision_policy']=='$DECISION_POLICY' and cfg['seats']['$W_NAME']=='$W_ID' and cfg['db']=='$ROOT/$P.db'" \
  || { result SETUP FAIL "fixture config content mismatch"; exit 3; }
echo '{"decision_policy":"'"$DECISION_POLICY"'","decision_ladder":[{"after_s":'"$RUNG0_S"'},{"after_s":'"$RUNG1_S"'},{"after_s":'"$RUNG2_S"'}],"decision_deadline_s":'"$DECISION_WINDOW_S"'}' | policy_eval | tee -a "$EV/driver.log" | grep -q ^PASS || { result SETUP FAIL "fixture policy ladder invalid"; exit 3; }
# Prep/binding as a SEPARATE bounded stage: worker+verifier via the LOCAL
# repaired prepare_live.py non-dry-run (real launches + binding + manifest;
# local indent fix vs frozen P6 original 462596ee…, see
# evidence/plan-repair/p6-indent-bug.md and prep-repro.sh), then explicit
# director/duty launches (same idle pattern), then a four-seat registry
# binding check. Agent-deck discovery uses explicit AGENTDECK_PROFILE +
# absolute paths (F2: no private-HOME export). Dry-run injected identity is
# never represented as live registry proof: only non-dry-run launches count.
log "prep stage: four fresh fixture seats"
run env AGENTDECK_PROFILE="$PROFILE" python3 "$PLANS/prepare_live.py" --profile "$PROFILE" --worker-name "$W_NAME" --verifier-name "$V_NAME" --manifest-out "$EV/prep-manifest.json" || { result PREP FAIL "worker/verifier prep failed"; exit 3; }
for pair in "$D_NAME:$D_ID" "$U_NAME:$U_ID"; do
  title="${pair%%:*}"
  run env AGENTDECK_PROFILE="$PROFILE" agent-deck launch "$ROOT" -t "$title" -cmd "$WAKE" -json || { result PREP FAIL "fixture launch failed: $title"; exit 3; }
done
REGJSON=$(env AGENTDECK_PROFILE="$PROFILE" agent-deck list --json) || { result PREP FAIL "registry unreadable"; exit 3; }
# Late-bound IDs resolve FROM the registry by exact title (never presupposed):
# four distinct titles, none a main seat, matching the prepare manifest.
python3 -c "
import json
titles = {'$W_NAME': 'W_ID', '$V_NAME': 'V_ID', '$D_NAME': 'D_ID', '$U_NAME': 'U_ID'}
d = json.loads('''$REGJSON''')
d = d if isinstance(d, list) else d.get('sessions', [])
main = {'0c933c75-1790000758', '493c0317-1790000758', 'a79067ca-1790000758', '56513e0e-1790000758'}
found = {}
for r in d:
    if r.get('archived'): continue
    if r.get('title') in titles: found[r['title']] = r.get('id')
assert len(found) == 4, 'launched titles missing: %s' % sorted(set(titles) - set(found))
assert len(set(found.values())) == 4, 'fixture IDs not distinct'
assert not (set(found.values()) & main), 'main seat adopted'
man = json.load(open('$EV/prep-manifest.json'))
assert man['worker']['session_id'] in found.values(), 'prepare manifest disagrees (worker)'
assert man['verifier']['session_id'] in found.values(), 'prepare manifest disagrees (verifier)'
pre = {'$W_NAME': '$W_ID', '$V_NAME': '$V_ID', '$D_NAME': '$D_ID', '$U_NAME': '$U_ID'}
for t, wid in pre.items():
    if wid and not wid.startswith('<'):
        assert found[t] == wid, 'resolved %s=%s contradicts signed %s' % (t, found[t], wid)
lines = ['%s=%s' % (v, found[t]) for t, v in titles.items()]
open('$EV/effective-ids.env', 'w').write('\n'.join(lines) + '\n')
print('binding ok:', sorted(found.values()))" || { result PREP FAIL "four-seat registry binding failed"; exit 3; }
# shellcheck disable=SC1090
. "$EV/effective-ids.env"
result PREP PASS "four fresh fixture seats bound (worker/verifier/director/duty)"
# Absolute-calendar cleanup armed and verified BEFORE fixture tasks.
run systemd-run --user --unit="$WALL" --timer-property=AccuracySec=1s --on-calendar="$(date -u -d @$DL_EPOCH '+%Y-%m-%d %H:%M:%S') UTC" /bin/bash "$PLANS/live20-plan.sh" "$INPUTS" cleanup \
  || { result SETUP FAIL "wall-stop not armed"; exit 3; }
[ "$(systemctl --user is-active "$WALL.timer")" = active ] && wall_ok || { result SETUP FAIL "wall-stop not active at deadline"; exit 3; }
trap cleanup EXIT
task() { # template file -> materialized per-QID file under the private ROOT
  guard "task $1 $2"; sed -e "s#{QID}#$2#g" -e "s#{ARTIFACTS}#$ROOT/art#g" "$PLANS/tasks/$1" > "$ROOT/tasks/$2-$1"; echo "$ROOT/tasks/$2-$1"; }
# F1: create AND start the run service and the outside-check service.
run mkdir -p "$SD"
_sub="s#%h/.local/bin/agent-loop#$A#g; s#%h/.config/agent-loop/%i.json#$CFG#g; s#agent-loop %i#agent-loop $P#g; s#%i#$P#g"
run sh -c "sed '$_sub' '$UNITS_SRC/agent-loop@.service' > '$SD/$U'"
run sh -c "sed '$_sub' '$UNITS_SRC/agent-loop-liveness@.service' > '$SD/$LU.service'"
run sh -c "sed '$_sub' '$UNITS_SRC/agent-loop-liveness@.timer' > '$SD/$LU.timer'"
run sh -c "sed '$_sub' '$UNITS_SRC/agent-loop-liveness-failed@.service' > '$SD/$LF.service'"
run systemctl --user daemon-reload
run systemctl --user start "$U"
run systemctl --user start "$LU.timer"
wait_for "run service active" 60 sh -c "systemctl --user is-active '$U'"
wait_for "outside check scheduled" 60 sh -c "systemctl --user is-active '$LU.timer'"
snap() { { echo "## $1 $(ts)"; } >>"$EV/snapshots.txt" 2>&1; }

# ---------------------------------------------------------------- live sequence
Q=D-$RUN; log "dispatch decision packages"
run mkdir -p "$ROOT/tasks"
run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task decision-worker.md "$Q")" --verify-task "@$(task decision-verify.md "$Q")" --duration 10m --verify-window 10m
wait_for "worker claim" 300 sh -c "$A status $C --json | python3 -c \"import json,sys; assert any(p['qid']=='$Q' for p in json.load(sys.stdin)['packages'])\""
wait_for "verifier claim" 300 sh -c "$A status $C --json | python3 -c \"import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert p.get('verdict')\""
log "decision entered (assert deadline + timer unit armed)"
run "$A" status $C --json | python3 -c "import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert p.get('decision',{}).get('deadline') and p.get('decision',{}).get('timer_unit'), 'no deadline/timer'" || { result DECISION FAIL "decision entered without deadline/timer unit"; exit 3; }
run "$A" stop $C
wait_for "stop marker exit 64" 60 sh -c "test -e '$ROOT/$P.db.stop'"
log "intentional stop marker AFTER authentic worker/verifier decision"
# F3: rungs read ACTUAL product JSON records (per-line JSONL), not invented strings.
wait_for "rung director" 60 sh -c "python3 -c 'import json; assert any(json.loads(l).get(\"rung\")==\"director\" for l in open(\"$ESC_LEDGER\") if l.strip())'"
wait_for "rung duty" 60 sh -c "python3 -c 'import json; assert any(json.loads(l).get(\"rung\")==\"duty\" for l in open(\"$ESC_LEDGER\") if l.strip())'"
wait_for "rung claude notice" 90 sh -c "python3 -c 'import json; assert any(json.loads(l).get(\"notice\")==\"claude\" for l in open(\"$ESC_LEDGER\") if l.strip())'"
printf 'rung:director\nrung:duty\nnotice:claude\n' >"$EV/rungs-want.txt"
python3 -c "
import json
seen = []
for l in open('$ESC_LEDGER'):
    l = l.strip()
    if not l: continue
    r = json.loads(l)
    if r.get('rung') == 'director': seen.append('rung:director')
    elif r.get('rung') == 'duty': seen.append('rung:duty')
    if r.get('notice') == 'claude': seen.append('notice:claude')
want = ['rung:director', 'rung:duty', 'notice:claude']
print(('PASS' if seen == want else 'FAIL') + ' ladder ' + str(seen))" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RUNGS FAIL "ladder order violated"; exit 3; }
grep -c "Signal" "$ESC_LEDGER" | grep -q ^0 || { result RUNGS FAIL "real Signal page during fixture run"; exit 3; }
# F3: capability ack by a MANDATORY EXPLICIT ACTOR (fixture duty), real cap file.
ACKF=$(ls "$ROOT"/caps/ack-$Q-*.claude 2>/dev/null | head -1)
[ -n "$ACKF" ] || { result ACK FAIL "no capability file produced for $Q"; exit 3; }
run "$A" decision-ack $C --qid "$Q" --by "$U_NAME" --cap-file "$ACKF" --next "duty owns the incident" --within 60s || { result ACK FAIL "explicit-actor capability ack refused"; exit 3; }
wait_for "recurrence same key" 180 sh -c "python3 -c 'import json; assert any(json.loads(l).get(\"reraised\") for l in open(\"$ESC_LEDGER\") if l.strip())'"
KEY1=$(python3 -c "import json; print([json.loads(l)['key'] for l in open('$ESC_LEDGER') if l.strip() and 'key' in json.loads(l)][0])")
recur_eval "$KEY1" "$(python3 -c "import json; print([json.loads(l)['key'] for l in open('$ESC_LEDGER') if l.strip() and 'key' in json.loads(l)][-1])")" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RECUR FAIL "recurrence key changed"; exit 3; }
# Authorized decide suppresses the future page (actual records, not absent text).
run "$A" decide $C --qid "$Q" --kind question_answered --ref "P13-live-$RUN" --reason "fixture decision"
wait_for "suppression" 120 sh -c "python3 -c 'import json; rs=[json.loads(l) for l in open(\"$ESC_LEDGER\") if l.strip()]; assert not any(r.get(\"page\")==\"$Q\" for r in rs)'"
suppress_eval "$Q" <"$ESC_LEDGER" | tee -a "$EV/driver.log" | grep -q ^PASS || { result DECIDE FAIL "page after decide"; exit 3; }
# Restart: REAL pass assertion (was assert True), no duplicates.
run "$A" start $C
wait_for "restart unit active" 90 sh -c "systemctl --user is-active '$U'"
run "$A" status $C --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('packages'), 'no packages after restart'" || { result RESTART FAIL "no status evidence after restart"; exit 3; }
nodup_eval "$Q" "$EV/driver.log" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RESTART FAIL "duplicate sends"; exit 3; }
result LIVE PASS "fixture decision ladder, ack/expiry/recurrence, decide suppression, restart no duplicates"
snap LIVE

log "all cases run; results in $EV/results.tsv"
if grep -qP '\t(FAIL|INCOMPLETE)\t' "$EV/results.tsv"; then log "NOT ALL PASS"; exit 1; fi
# cleanup runs from the trap
