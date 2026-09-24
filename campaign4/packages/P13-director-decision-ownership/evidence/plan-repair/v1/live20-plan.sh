#!/bin/bash
# P13 live20 decision-ownership plan (stand-in author; preserved outline as input).
# Runs ONLY after Tern signs the filled INPUTS hash. Offline rehearsal:
#   DRY=1 plans/live20-plan.sh plans/live-inputs.template.env   (filled copy)
# Private HOME/ROOT isolate every effect. No live fixture launches, no service
# changes/reloads, no real wakes/Signal, no shared ledger writes in rehearsal:
# stubs live in a private temporary HOME only. Failed commands fail the stage.
#
# Sequence: prep/binding (P6 prepare_live.py pattern + agent-deck registry) ->
# dispatch worker/verifier decision packages (fixture ladder 0/20/40, generic
# policy, window 60s) -> genuine claims/turns -> decision entered -> stop marker
# (exit 64) -> rungs while stopped -> capability ack/expiry/recurrence ->
# authorized decide -> suppression -> restart (no duplicates) -> cleanup.
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}; DRY=${DRY:-0}
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
PLANS=$PKG/plans
# shellcheck disable=SC1090
. "$INPUTS"
for v in RUN ROOT LIVE_DEADLINE PROFILE WAKE STREAMS BIN_SRC BIN_SHA W_NAME W_ID V_NAME V_ID D_NAME D_ID U_NAME U_ID RUNG0_S RUNG1_S RUNG2_S DECISION_WINDOW_S DECISION_POLICY ESC_LEDGER NOTIFY_CLAUDE RESOLVE_CMD TICKET_STUB ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
  val=${!v:-}
  if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
for id in $W_ID $V_ID $D_ID $U_ID; do
  case " 0c933c75-1790000758 493c0317-1790000758 a79067ca-1790000758 56513e0e-1790000758 " in *" $id "*) echo "main seat $id is forbidden" >&2; exit 2;; esac
done
[ "$(printf '%s\n' "$W_ID" "$V_ID" "$D_ID" "$U_ID" | sort -u | wc -l)" -eq 4 ] || { echo "fixture IDs must be four distinct values" >&2; exit 2; }
DL_EPOCH=$(date -u -d "$LIVE_DEADLINE" +%s 2>/dev/null) || { echo "LIVE_DEADLINE invalid" >&2; exit 2; }
# Caller HOME/PATH must not leak: pin private HOME for every child; default PATH
# is replaced, never inherited into escalation paths.
export HOME="$ROOT/home"
export PATH="/usr/bin:/bin"
export AGENTDECK_PROFILE="$PROFILE"
P=p13d$RUN
A=$ROOT/bin/agent-loop
CFG=$ROOT/$P.json
C="--config $CFG"
U=agent-loop-$P.service
LU=agent-loop-liveness-$P
SD=$ROOT/systemd/user
EV=${EV_DIR:-$PKG/evidence/plan-standin/$RUN}
WALL=p13live-wallstop-$RUN
SCOPE=p13live-driver-$RUN
mkdir -p "$EV"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/driver.log"; }
_now() { date +%s; }
guard() { [ -n "${TEARDOWN:-}" ] || [ "$DRY" = 1 ] || [ "$(_now)" -lt "$DL_EPOCH" ] && return 0
  echo "$(ts) DEADLINE: refused: $*" >>"$EV/driver.log"
  result DEADLINE INCOMPLETE "refused at $(ts): $*"; exit 3; }
run() { guard "$@"; log "+ $*"; if [ "$DRY" = 1 ]; then return 0; fi; "$@" >>"$EV/driver.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
out() { echo "$(ts) + $* (captured)" >>"$EV/driver.log"; if [ "$DRY" = 1 ]; then echo "DRY"; return 0; fi; "$@" 2>>"$EV/driver.log"; }
result() { local st=$2; [ "$DRY" = 1 ] && st=DRY; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/results.tsv"; }
. "$PLANS/decision-evaluators.sh"
wait_for() { local label=$1 limit=$2; shift 2; local t0; t0=$(date +%s)
  if [ "$DRY" = 1 ]; then log "wait_for $label ${limit}s: $*"; return 0; fi
  while ! "$@" >/dev/null 2>&1; do
    if [ $(( $(date +%s) - t0 )) -ge "$limit" ]; then log "timeout waiting for $label"; result "wait:$label" INCOMPLETE "not reached in ${limit}s"; return 1; fi; sleep 2; done
  log "reached $label after $(( $(date +%s) - t0 ))s"; }
cleanup() {
  trap - EXIT; TEARDOWN=1
  if ! mkdir "$EV/cleanup.lock" 2>/dev/null; then log "cleanup already ran"; return 0; fi
  log "cleanup (exact IDs)"
  mkdir -p "$EV/archive"
  if [ "$DRY" != 1 ]; then
    [ -d "$ROOT/caps" ] && tar -cf "$EV/archive/caps.tar" -C "$ROOT" caps
    cp -a "$ROOT"/. "$EV/archive/" 2>/dev/null
  fi
  run systemctl --user stop "$LU.timer" "$LU.service" "$U"
  for t in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" 2>/dev/null | awk '{print $1}'); do run systemctl --user stop "$t"; done
  run systemctl --user reset-failed "agent-loop-$P*" "$LU*" 2>/dev/null
  run rm -f "$SD/$U" "$SD/$LU.service" "$SD/$LU.timer"
  run systemctl --user daemon-reload
  for id in $W_ID $V_ID $D_ID $U_ID; do run agent-deck session stop "$id"; run agent-deck session remove "$id"; done
  run systemctl --user stop "$WALL.timer"
  # capability-secret cleanup only after bounded archive exists above
  if [ "$DRY" != 1 ] && [ -f "$EV/archive/caps.tar" ]; then run rm -rf "$ROOT/caps"; fi
  local left=""
  if [ "$DRY" != 1 ]; then
    for id in $W_ID $V_ID $D_ID $U_ID; do run agent-deck list --json | grep -q "$id" && left="$left seat $id;"; done
    for u in "$LU.timer" "$U"; do [ "$(systemctl --user is-active "$u" 2>/dev/null)" = active ] && left="$left unit $u active;"; done
    [ -d "$ROOT/caps" ] && left="$left caps dir remains;"
  fi
  if [ -n "$left" ]; then result CLEANUP FAIL "unresolved:$left"; return 1; fi
  log "cleanup done"
}
wall_ok() { [ "$(systemctl --user show "$WALL.timer" -p TimersCalendar --timestamp=unix --value 2>/dev/null | grep -o 'next_elapse=@[0-9]*' | cut -d= -f2)" = "@$DL_EPOCH" ]; }
if [ "$MODE" = cleanup ]; then TEARDOWN=1; cleanup; exit 0; fi

# ---------------------------------------------------------------- setup
log "P13 live $RUN, inputs sha256 $(sha256sum "$INPUTS" | cut -d' ' -f1)"
if [ -e "$ROOT" ] && [ "$DRY" != 1 ]; then result SETUP INCOMPLETE "private root exists"; exit 3; fi
run mkdir -p "$ROOT/bin" "$ROOT/home" "$ROOT/art" "$ROOT/claims" "$ROOT/caps"
run chmod 700 "$ROOT/caps"
run install -m 755 "$BIN_SRC" "$A"
if [ "$DRY" != 1 ] && [ "$(sha256sum "$A" | cut -d' ' -f1)" != "$BIN_SHA" ]; then result SETUP FAIL "binary hash mismatch"; exit 3; fi
# Private escalation sinks + stubs (never shared ledger/pager).
run mkdir -p "$(dirname "$ESC_LEDGER")" "$(dirname "$NOTIFY_CLAUDE")" "$(dirname "$RESOLVE_CMD")"
run sh -c "printf '#!/bin/bash\necho stub-ticket \$@ >>$TICKET_STUB\n' > '$NOTIFY_CLAUDE' && chmod +x '$NOTIFY_CLAUDE'"
# Private candidate adapters (exact reviewed hashes; installed only at signed promotion).
run install -m 755 "$ADAPTER_WATCH_SRC" "$ROOT/bin/escalation-watch"
run install -m 755 "$ADAPTER_RESOLVE_SRC" "$ROOT/bin/escalation-resolve"
if [ "$DRY" != 1 ]; then
  [ "$(sha256sum "$ROOT/bin/escalation-watch" | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] || { result SETUP FAIL "watch adapter hash mismatch"; exit 3; }
  [ "$(sha256sum "$ROOT/bin/escalation-resolve" | cut -d' ' -f1)" = "$ADAPTER_RESOLVE_SHA" ] || { result SETUP FAIL "resolve adapter hash mismatch"; exit 3; }
fi
# Fixture decision config: generic policy + accelerated ladder (declared deviation
# for signature; production required 0/300/600 validated offline separately).
guard "write fixture config"; [ "$DRY" = 1 ] && log "+ write config $CFG" || python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "$P", "profile": "$PROFILE", "db": "$ROOT/$P.db",
 "decision_policy": "$DECISION_POLICY",
 "decision_deadline_s": $DECISION_WINDOW_S,
 "decision_ladder": [{"after_s": $RUNG0_S, "seat": "$D_NAME"}, {"after_s": $RUNG1_S, "seat": "$U_NAME"},
  {"after_s": $RUNG2_S, "exec": ["$NOTIFY_CLAUDE", "decision"], "ledger": "$ESC_LEDGER", "ledger_kind": "decision", "resolve_cmd": ["$ROOT/bin/escalation-resolve"]}],
 "decision_responders": ["claude"]}, open(sys.argv[1], "w"), indent=1)
PY
[ "$DRY" = 1 ] || out "$CFG" | python3 -c "import json,sys; cfg=json.load(open('$CFG')); assert cfg['decision_policy']=='$DECISION_POLICY'" \
  || { result SETUP FAIL "fixture config policy mismatch"; exit 3; }
echo '{"decision_policy":"'"$DECISION_POLICY"'","decision_ladder":[{"after_s":'"$RUNG0_S"'},{"after_s":'"$RUNG1_S"'},{"after_s":'"$RUNG2_S"'}],"decision_deadline_s":'"$DECISION_WINDOW_S"'}' | policy_eval | tee -a "$EV/driver.log" | grep -q ^PASS || { result SETUP FAIL "fixture policy ladder invalid"; exit 3; }
# Prep/binding: fresh fixture seats via the P6 prepare pattern (live execution needs
# the separately signed prep release; rehearsal uses DRY), then registry preflight.
if [ "$DRY" != 1 ]; then
  run python3 /home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation/src/prepare_live.py --profile "$PROFILE" --worker "$W_NAME" --verifier "$V_NAME" --out "$EV/launch-manifest.json" || { result SETUP FAIL "fixture seat prep failed"; exit 3; }
fi
# Absolute-calendar cleanup armed and verified BEFORE fixture tasks.
run systemd-run --user --unit="$WALL" --timer-property=AccuracySec=1s --on-calendar="$(date -u -d @$DL_EPOCH '+%Y-%m-%d %H:%M:%S') UTC" --setenv=PATH="$PATH" /bin/bash "$PLANS/live20-plan.sh" "$INPUTS" cleanup \
  || { result SETUP FAIL "wall-stop not armed"; exit 3; }
if [ "$DRY" != 1 ] && { [ "$(systemctl --user is-active "$WALL.timer")" != active ] || ! wall_ok; }; then result SETUP FAIL "wall-stop not active at deadline"; exit 3; fi
trap cleanup EXIT
snap() { { echo "## $1 $(ts)"; } >>"$EV/snapshots.txt" 2>&1; }
task() { # template file -> materialized per-QID file under the private ROOT
  guard "task $1 $2"; sed -e "s#{QID}#$2#g" -e "s#{ARTIFACTS}#$ROOT/art#g" "$PLANS/tasks/$1" > "$ROOT/tasks/$2-$1"; echo "$ROOT/tasks/$2-$1"; }

# ---------------------------------------------------------------- live sequence
Q=D-$RUN; log "dispatch decision packages"
run mkdir -p "$ROOT/tasks"
run "$A" dispatch $C --qid "$Q" --worker "$W_NAME" --verifier "$V_NAME" --task "@$(task decision-worker.md "$Q")" --verify-task "@$(task decision-verify.md "$Q")" --duration 10m --verify-window 10m
wait_for "worker claim" 300 sh -c "$A status $C --json | python3 -c \"import json,sys; assert any(p['qid']=='$Q' for p in json.load(sys.stdin)['packages'])\""
wait_for "verifier claim" 300 sh -c "$A status $C --json | python3 -c \"import json,sys; p=[p for p in json.load(sys.stdin)['packages'] if p['qid']=='$Q'][0]; assert p.get('verdict')\""
log "decision entered (assert deadline + timer unit armed)"
run "$A" stop $C
wait_for "stop marker exit 64" 60 sh -c "test -e '$ROOT/$P.db.stop'"
log "intentional stop marker AFTER authentic worker/verifier decision"
# Rungs while stopped: director wake at +0, duty at +20, labelled Claude notice at +40.
# DRY rehearsal has no ledger: rung order + no-Signal are covered by the offline
# evaluator negatives instead (rehearse.sh), never asserted here in DRY.
wait_for "rung director" 60 sh -c "grep -q 'rung:director' '$ESC_LEDGER'"
wait_for "rung duty" 60 sh -c "grep -q 'rung:duty' '$ESC_LEDGER'"
wait_for "rung claude notice" 90 sh -c "grep -q 'notice:claude' '$ESC_LEDGER'"
if [ "$DRY" = 1 ]; then log "DRY: rung order + no-Signal deferred to offline negatives";
else
rung_order_eval "director,duty,claude" <"$ESC_LEDGER" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RUNGS FAIL "ladder order violated"; exit 3; }
[ "$DRY" = 1 ] || grep -c "Signal" "$ESC_LEDGER" | grep -q ^0 || { result RUNGS FAIL "real Signal page during fixture run"; exit 3; }
fi
# Capability ack (60 s), expiry, same-key recurrence; quiet absent obligations.
# DRY rehearsal has no live artifacts: ack/expiry/recurrence/decide checks are
# covered by the offline evaluator negatives instead (rehearse.sh).
ACKF="$ROOT/caps/ack-$Q.json"
if [ "$DRY" = 1 ]; then log "DRY: ack/expiry/recurrence/decide deferred to offline negatives";
else
wait_for "capability ack" 120 sh -c "test -e '$ACKF'"
ack_eval "$ACKF" "$Q" "$U_NAME" | tee -a "$EV/driver.log" | grep -q ^PASS || { result ACK FAIL "capability ack invalid"; exit 3; }
KEY1=$(python3 -c "import json; print(json.load(open('$ESC_LEDGER')).get('key',''))" 2>/dev/null)
wait_for "recurrence same key" 180 sh -c "grep -q 'recur:$KEY1' '$ESC_LEDGER'"
recur_eval "$KEY1" "$(grep 'recur:' '$ESC_LEDGER' | tail -1 | cut -d: -f2)" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RECUR FAIL "recurrence key changed"; exit 3; }
# Authorized decide suppresses the future page.
run "$A" decide $C --qid "$Q" --kind question_answered --ref "P13-live-$RUN" --reason "fixture decision"
wait_for "suppression" 120 sh -c "! grep -q 'page:$Q' '$ESC_LEDGER'"
suppress_eval "$Q" <"$ESC_LEDGER" | tee -a "$EV/driver.log" | grep -q ^PASS || { result DECIDE FAIL "page after decide"; exit 3; }
# Restart: no duplicates, at most one labelled repeat per ambiguous stage.
run "$A" start $C
wait_for "restart pass" 90 sh -c "$A status $C --json | python3 -c 'import json,sys; assert True'"
nodup_eval "$Q" "$EV/driver.log" | tee -a "$EV/driver.log" | grep -q ^PASS || { result RESTART FAIL "duplicate sends"; exit 3; }
result LIVE PASS "fixture decision ladder, ack/expiry/recurrence, decide suppression, restart no duplicates"
fi
snap LIVE

log "all cases run; results in $EV/results.tsv"
if grep -qP '\t(FAIL|INCOMPLETE)\t' "$EV/results.tsv"; then log "NOT ALL PASS"; exit 1; fi
# cleanup runs from the trap
