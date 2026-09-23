#!/bin/bash
# P10 stage D: cutover of campaign4 from the old scripts to agent-loop, the first
# real package, and rollback. Only after corvid's live PASS and Tern's signature
# of the filled inputs (sha256 of CUTOVER_INPUTS).
#
#   cutover.sh INPUTS.env capture     record the exact prior state (restorable)
#   cutover.sh INPUTS.env switch      drain old effects, install and start agent-loop, verify
#   cutover.sh INPUTS.env handoff     dispatch P10-production-handoff-1 through agent-loop
#   cutover.sh INPUTS.env rollback    drain agent-loop effects, restore the old owners
#   DRY=1 ... prints every command, runs none.
# Paths are absolute; no %h. The TSV ledger is archived, never imported or edited.
set -uo pipefail
INPUTS=$(readlink -f "$1"); CMD=${2:?capture|switch|handoff|rollback}; DRY=${DRY:-0}
# shellcheck disable=SC1090
. "$INPUTS"
for v in CUT_RUN QUALIFIED_BIN QUALIFIED_SHA KILN_ID CORVID_ID TERN_ID CAIRN_ID; do
  val=${!v:-}; if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
H=/home/bmosher
PKG=$H/memory-bake-off/campaign4/packages/P10-go-requalification-cutover
EV=${EV_DIR:-$PKG/cutover-$CUT_RUN}; PRE=$EV/pre   # EV_DIR only for offline rehearsal
SD=$H/.config/systemd/user
BIN=$H/.local/bin/agent-loop
PREV=$H/.local/bin/agent-loop.prev-c124d82
CFG=$H/.config/agent-loop/campaign4.json
DB=$H/.local/share/agent-loop/campaign4.db
C="--config $CFG"
OLD_TIMERS="openwork.timer coax-dry.timer shadow-watch.timer"
OLD_SERVICES="openwork.service coax-dry.service shadow-watch.service campaign4-watch.service"
NEW_RUN=agent-loop@campaign4.service
NEW_LIVE=agent-loop-liveness@campaign4
UNITS_SRC=$(dirname "$QUALIFIED_BIN")/../examples/systemd-unqualified
mkdir -p "$EV" "$PRE"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/cutover.log"; }
run() { log "+ $*"; [ "$DRY" = 1 ] && return 0; "$@" >>"$EV/cutover.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
fail() { log "FAILED: $*"; printf '%s\tFAIL\t%s\n' "$CMD" "$*" >>"$EV/results.tsv"; exit 3; }
ok() { printf '%s\tPASS\t%s\t%s\n' "$CMD" "$(ts)" "$*" | tee -a "$EV/results.tsv"; }
# drain UNIT...: wait (bounded 120 s) until each service is not active, i.e. a callback
# already running finishes; then stop any still active. Stopped timers alone settle nothing.
drain() { for s in "$@"; do
  local t0; t0=$(date +%s)
  while [ "$DRY" != 1 ] && [ "$(systemctl --user is-active "$s")" = active -o "$(systemctl --user is-active "$s")" = activating ]; do
    [ $(( $(date +%s) - t0 )) -ge 120 ] && { run systemctl --user stop "$s"; break; }; sleep 2; done
  log "drained $s: $(systemctl --user is-active "$s" 2>&1)"; done; }

capture() {
  for u in $OLD_TIMERS $OLD_SERVICES campaign4-watch.timer; do
    { echo "== $u"; systemctl --user cat "$u"; echo "enabled=$(systemctl --user is-enabled "$u" 2>&1)"; echo "active=$(systemctl --user is-active "$u" 2>&1)";
      systemctl --user show "$u" -p TimersMonotonic,TimersCalendar,NextElapseUSecRealtime; } >>"$PRE/units.txt" 2>&1; done
  sha256sum $H/.config/agent-deck/openwork $H/.config/agent-deck/campaign4-watch $H/.config/agent-deck/shadow-watch "$BIN" >"$PRE/hashes.txt"
  AGENTDECK_PROFILE=campaign4 agent-deck list --json >"$PRE/registry.json"
  cp $H/memory-bake-off/campaign4/control-events.tsv "$PRE/control-events.tsv"
  tail -n 100 $H/.local/share/agent-deck/wake-send.log >"$PRE/wake-send.txt"
  systemctl --user list-timers --all --no-pager >"$PRE/timers.txt"
  ok "prior state captured in $PRE"
}

open_dispatches() { # DISPATCHED rows in the TSV with no later result row for the same qid
  python3 - $H/memory-bake-off/campaign4/control-events.tsv <<'PY'
import sys
results = {"COMPLETED","COMPLETE","INCOMPLETE","PARTIAL","PASS","FAIL","ACCEPTED","BLOCKED","CANCELLED","RETIRED",
           "EXHAUSTED","SUPERSEDED","WITHDRAWN","FROZEN","RESOLVED","INFRA_FAILURE","PREPARED","TERMINATED"}
openq = {}
for line in open(sys.argv[1]):
    f = line.rstrip("\n").split("\t")
    if len(f) < 5: continue
    if f[3] == "DISPATCHED": openq[f[2]] = line.strip()
    elif f[3] in results: openq.pop(f[2], None)
for q, l in openq.items(): print(l)
PY
}

switch() {
  [ -s "$PRE/units.txt" ] || fail "run capture first"
  [ -e "$DB" ] && [ "$DRY" != 1 ] && fail "the new ledger $DB already exists"
  [ "$DRY" = 1 ] || [ "$(sha256sum "$QUALIFIED_BIN" | cut -d' ' -f1)" = "$QUALIFIED_SHA" ] || fail "qualified binary hash mismatch"
  o=$(open_dispatches); if [ -n "$o" ] && [ "$DRY" != 1 ]; then echo "$o" >"$EV/open-dispatches.txt"; fail "open dispatches in the TSV (see open-dispatches.txt): return to Tern"; fi
  # 1. old effect owners off, running callbacks drained
  run systemctl --user disable --now $OLD_TIMERS
  run systemctl --user stop campaign4-watch.timer
  drain $OLD_SERVICES
  for u in $OLD_TIMERS campaign4-watch.timer; do [ "$DRY" = 1 ] || [ "$(systemctl --user is-active "$u")" != active ] || fail "$u still active"; done
  run "$H/.config/agent-deck/wake" "$CAIRN_ID" "[P10 cutover $CUT_RUN] Your controller role ends now: no dispatch, no ledger rows, no deadline timers. You stay duty and liveness owner for agent-loop (acknowledge liveness incidents with the command they carry)."
  # 2. qualified binary, config, units
  run install -m 755 "$BIN" "$PREV"
  run install -m 755 "$QUALIFIED_BIN" "$BIN"
  run mkdir -p "$(dirname "$CFG")" "$(dirname "$DB")" $H/.local/share/agent-loop/campaign4/claims
  [ "$DRY" = 1 ] && log "+ write $CFG" || python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "campaign4", "profile": "campaign4", "wake": "$H/.config/agent-deck/wake", "db": "$DB",
  "stream_dir": "$H/.config/agent-deck/acp-stream", "claims_dir": "$H/.local/share/agent-loop/campaign4/claims",
  "artifacts_dir": "$H/memory-bake-off/campaign4", "director": "tern", "duty": "cairn",
  "seats": {"kiln": "$KILN_ID", "corvid": "$CORVID_ID", "tern": "$TERN_ID", "cairn": "$CAIRN_ID"},
  "bin": "$BIN", "unit": "$NEW_RUN"}, open(sys.argv[1], "w"), indent=1)
PY
  run cp "$UNITS_SRC/agent-loop@.service" "$UNITS_SRC/agent-loop-liveness@.service" "$UNITS_SRC/agent-loop-liveness@.timer" "$SD/"
  run systemctl --user daemon-reload
  run "$BIN" check $C || { log "binding check failed: rolling back"; rollback; exit 3; }
  run systemctl --user enable --now "$NEW_RUN" "$NEW_LIVE.timer"
  # 3. verify: a pass from the current invocation, then the outside check says rest
  local t0; t0=$(date +%s)
  until [ "$DRY" = 1 ] || "$BIN" expose $C --json | grep -q '"freshness": "last loop pass'; do
    [ $(( $(date +%s) - t0 )) -ge 60 ] && { log "no pass within 60 s: rolling back"; rollback; exit 3; }; sleep 5; done
  run systemctl --user start "$NEW_LIVE.service"
  [ "$DRY" = 1 ] || grep -q '"state": "rest"' "$DB.liveness.json" || { log "check not rest: rolling back"; rollback; exit 3; }
  run systemctl --user list-timers --all --no-pager
  ok "old owners off and drained; agent-loop serving; outside check rest; one owner"
}

handoff() {
  run "$BIN" dispatch $C --qid P10-production-handoff-1 --worker kiln --verifier corvid --duration 20m --verify-window 10m \
    --task "@$PKG/plans/tasks/handoff-task.md" --verify-task "@$PKG/plans/tasks/handoff-verify.md"
  ok "P10-production-handoff-1 dispatched through agent-loop; Tern decides with: $BIN decide $C --qid P10-production-handoff-1 --kind question_answered --ref <record> --reason <text>"
}

rollback() {
  # 1. archive and reconcile what agent-loop owns
  mkdir -p "$EV/rollback"
  [ "$DRY" = 1 ] || "$BIN" expose $C --json >"$EV/rollback/expose.json" 2>&1
  [ "$DRY" = 1 ] || cp -a "$DB" "$DB-wal" "$DB-shm" "$DB.liveness.json" $H/.local/share/agent-loop/campaign4/claims "$EV/rollback/" 2>/dev/null
  # 2. candidate effects off; its running callbacks drained
  run systemctl --user disable --now "$NEW_RUN" "$NEW_LIVE.timer"
  cb_timers=$(systemctl --user list-units --all --plain --no-legend 'agent-loop-campaign4-*.timer' 2>/dev/null | awk '{print $1}')
  for t in $cb_timers; do run systemctl --user stop "$t"; done
  drain "$NEW_LIVE.service" $(systemctl --user list-units --all --plain --no-legend 'agent-loop-campaign4-*.service' 2>/dev/null | awk '{print $1}')
  # 3. open agent-loop packages go to cairn as explicit items (claim paths included); nothing re-sent
  [ "$DRY" = 1 ] || python3 - "$EV/rollback/expose.json" >"$EV/rollback/open-items.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
print(json.dumps([p for p in v.get("packages", []) if p.get("step") != "closed"], indent=1))
PY
  # 4. previous binary and old owners back
  [ -e "$PREV" ] && run install -m 755 "$PREV" "$BIN"
  run systemctl --user enable --now $OLD_TIMERS
  run systemd-run --user --unit=campaign4-watch --on-active=45min --on-unit-active=45min $H/.config/agent-deck/campaign4-watch
  run "$H/.config/agent-deck/wake" "$CAIRN_ID" "[P10 cutover $CUT_RUN] ROLLBACK: your controller role is restored. Open agent-loop items to adopt (no resend; check each seat first): $EV/rollback/open-items.json"
  # 5. one owner
  for u in $OLD_TIMERS; do [ "$DRY" = 1 ] || [ "$(systemctl --user is-active "$u")" = active ] || fail "$u not active after rollback"; done
  [ "$DRY" = 1 ] || [ "$(systemctl --user is-active "$NEW_RUN")" != active ] || fail "agent-loop still active after rollback"
  ok "rolled back: old owners active, agent-loop off, open items handed to cairn"
}

case "$CMD" in capture) capture;; switch) switch;; handoff) handoff;; rollback) rollback;; *) echo "unknown $CMD" >&2; exit 2;; esac
