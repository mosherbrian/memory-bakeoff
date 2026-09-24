#!/bin/bash
# P12 stage D: cutover of campaign4 from the old scripts to agent-loop, the first
# real package, and rollback. Only after corvid's live PASS and Tern's signature
# of the filled inputs (sha256 of CUTOVER_INPUTS).
#
#   cutover.sh INPUTS.env capture     record the exact prior state (restorable)
#   cutover.sh INPUTS.env switch      drain old effects, install and start agent-loop, verify
#   cutover.sh INPUTS.env handoff     dispatch P12-production-handoff-1 through agent-loop
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
H=${CUT_HOME:-/home/bmosher}   # CUT_HOME: ONLY for offline rehearsal (a sandbox home with stub PATH); never in the signed run
PKG=/home/bmosher/memory-bake-off/campaign4/packages/P12-timeout-ownership-live-closure
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
# P12-cutover-plan-closure-1: all FOUR qualified units, including the check's OnFailure handler (checker-ownership).
UNITS="agent-loop@.service agent-loop-liveness@.service agent-loop-liveness@.timer agent-loop-liveness-failed@.service"
NEW_FAIL=agent-loop-liveness-failed@campaign4.service
. "$PKG/plans/live-checks.sh"   # pass_eval, healthy_eval (the live-qualified predicates)
mkdir -p "$EV" "$PRE"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/cutover.log"; }
run() { log "+ $*"; [ "$DRY" = 1 ] && return 0; "$@" >>"$EV/cutover.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
must() { run "$@" || fail "required command failed: $*"; }   # a failed required command never ends a stage PASS
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
  # exact restorable state: one row per old unit (rollback restores exactly this, nothing more)
  : >"$PRE/state.tsv"; for u in $OLD_TIMERS campaign4-watch.timer; do
    printf '%s\t%s\t%s\n' "$u" "$(systemctl --user is-enabled "$u" 2>/dev/null || true)" "$(systemctl --user is-active "$u" 2>/dev/null || true)" >>"$PRE/state.tsv"; done
  # existing unit files that switch would replace are kept byte for byte
  mkdir -p "$PRE/units-prev"; : >"$PRE/units-prev.list"
  for u in $UNITS; do [ -e "$SD/$u" ] && { cp -a "$SD/$u" "$PRE/units-prev/$u"; echo "$u" >>"$PRE/units-prev.list"; }; done
  [ -e "$CFG" ] && cp -a "$CFG" "$PRE/config-prev.json"
  cli_preflight
  ok "prior state captured in $PRE (state.tsv: $(wc -l <"$PRE/state.tsv") units; $(wc -l <"$PRE/units-prev.list") existing unit files kept)"
}

# cli_preflight: the qualified release has every command the cutover, handoff and operator need, and all four
# units with the OnFailure wiring and the exact handler command. Read-only; fails the stage.
cli_preflight() {
  # each command is asked directly (the top-level help omits some, e.g. timeout-ack): a known command answers
  # `-h` with "Usage of CMD:"; an unknown one prints the top-level usage. Output captured whole.
  local c o
  for c in run dispatch decide claim status expose stop start liveness checker-failed liveness-ack timeout-ack check; do
    o=$("$QUALIFIED_BIN" "$c" -h 2>&1); case "$o" in *"Usage of $c:"*) ;; *) fail "qualified binary lacks the '$c' command";; esac; done
  o=$("$QUALIFIED_BIN" version 2>&1); case "$o" in ""|"usage: agent-loop COMMAND"*) fail "qualified binary lacks the 'version' command";; esac
  for u in $UNITS; do [ -s "$UNITS_SRC/$u" ] || fail "qualified unit $u missing from $UNITS_SRC"; done
  grep -qx 'OnFailure=agent-loop-liveness-failed@%i.service' "$UNITS_SRC/agent-loop-liveness@.service" || fail "the check unit lacks OnFailure=agent-loop-liveness-failed@%i.service"
  grep -qx 'ExecStart=%h/.local/bin/agent-loop checker-failed --config %h/.config/agent-loop/%i.json --unit agent-loop-liveness@%i.service' "$UNITS_SRC/agent-loop-liveness-failed@.service" || fail "the handler unit does not run the expected checker-failed command"
  for u in agent-loop@.service agent-loop-liveness@.service; do grep -q '^ExecStart=%h/.local/bin/agent-loop ' "$UNITS_SRC/$u" || fail "$u does not run %h/.local/bin/agent-loop (= $BIN)"; done
  log "cli/unit preflight ok: commands, 4 units, OnFailure wiring, handler command"
}

# seat_identity: every seat id in the inputs is registered in the campaign4 profile under its role title
# (runtime identity mapping for the config and every message). Read-only; fails the stage.
seat_identity() {
  local reg; reg=$(AGENTDECK_PROFILE=campaign4 agent-deck list --json 2>&1)
  printf '%s' "$reg" | python3 -c '
import json, sys
rows = {r.get("id"): (r.get("title") or "") for r in json.load(sys.stdin)}
want = dict(zip(sys.argv[1::2], sys.argv[2::2])); bad = []
for i, t in want.items():
    if i not in rows: bad.append("%s (%s) not registered" % (i, t))
    elif not rows[i].startswith(t): bad.append("%s is %r, not %s" % (i, rows[i], t))
print("; ".join(bad)); sys.exit(1 if bad else 0)' "$KILN_ID" kiln "$CORVID_ID" corvid "$TERN_ID" tern "$CAIRN_ID" cairn >"$EV/seat-identity.txt" 2>&1 \
    || fail "seat identity mismatch in profile campaign4: $(cat "$EV/seat-identity.txt")"
  log "seat identity ok: kiln/corvid/tern/cairn ids registered in campaign4 under their titles"
}

open_dispatches() { # DISPATCHED rows in the TSV with no later result row for the same qid
  python3 - $H/memory-bake-off/campaign4/control-events.tsv <<'PY'
import sys
results = {"COMPLETED","COMPLETE","INCOMPLETE","PARTIAL","PASS","FAIL","ACCEPTED","BLOCKED","CANCELLED","RETIRED",
           "EXHAUSTED","SUPERSEDED","WITHDRAWN","FROZEN","RESOLVED","INFRA_FAILURE","PREPARED","TERMINATED",
           "NOT-READY","BOUNDED-FAIL","CLOSED"}   # terminal verbs the P11/P12 reviews actually use (ledger 2026-09-23/24)
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
  cli_preflight
  seat_identity
  must systemctl --user disable --now $OLD_TIMERS
  run systemctl --user stop campaign4-watch.timer   # transient; may already be absent
  drain $OLD_SERVICES
  # no old effect owner may still run before a new one starts
  for u in $OLD_TIMERS campaign4-watch.timer $OLD_SERVICES; do [ "$DRY" = 1 ] || case "$(systemctl --user is-active "$u" 2>/dev/null)" in active|activating) fail "$u still active";; esac; done
  run env AGENTDECK_PROFILE=campaign4 "$H/.config/agent-deck/wake" "$CAIRN_ID" "[P12 cutover $CUT_RUN] Your controller role ends now: no dispatch, no ledger rows, no deadline timers. You stay duty and liveness owner for agent-loop (acknowledge liveness incidents with the command they carry)."
  # 2. qualified binary, config, units
  must install -m 755 "$BIN" "$PREV"
  must install -m 755 "$QUALIFIED_BIN" "$BIN"
  run mkdir -p "$(dirname "$CFG")" "$(dirname "$DB")" $H/.local/share/agent-loop/campaign4/claims
  [ "$DRY" = 1 ] && log "+ write $CFG" || python3 - "$CFG" <<PY
import json, sys
json.dump({"project": "campaign4", "profile": "campaign4", "wake": "$H/.config/agent-deck/wake", "db": "$DB",
  "stream_dir": "$H/.config/agent-deck/acp-stream", "claims_dir": "$H/.local/share/agent-loop/campaign4/claims",
  "artifacts_dir": "$H/memory-bake-off/campaign4", "director": "tern", "duty": "cairn",
  "seats": {"kiln": "$KILN_ID", "corvid": "$CORVID_ID", "tern": "$TERN_ID", "cairn": "$CAIRN_ID"},
  "bin": "$BIN", "unit": "$NEW_RUN"}, open(sys.argv[1], "w"), indent=1)
PY
  for u in $UNITS; do must cp "$UNITS_SRC/$u" "$SD/$u"; [ "$DRY" = 1 ] || cmp -s "$UNITS_SRC/$u" "$SD/$u" || { log "installed $u differs from the release: rolling back"; rollback; exit 3; }; done
  must systemctl --user daemon-reload
  [ "$DRY" = 1 ] || [ "$(systemctl --user show "$NEW_LIVE.service" -p OnFailure --value)" = "$NEW_FAIL" ] || { log "systemd does not wire $NEW_LIVE.service OnFailure=$NEW_FAIL: rolling back"; rollback; exit 3; }
  run "$BIN" check $C || { log "binding check failed: rolling back"; rollback; exit 3; }
  local t0; t0=$(date +%s)
  run systemctl --user enable --now "$NEW_RUN" "$NEW_LIVE.timer" || { log "enable failed: rolling back"; rollback; exit 3; }
  # 3. verify with the live-qualified predicates: the ledger's own pass record is from after t0 by the unit's CURRENT
  # invocation and main pid; then a completed outside check (unit result success) reads rest, checked after t0.
  until [ "$DRY" = 1 ] || python3 -c 'import sqlite3,sys; c=sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True, timeout=1); print(c.execute("select value from driver_kv where key=?", ("loop-pass",)).fetchone()[0])' "$DB" 2>/dev/null \
      | pass_eval "$t0" "$(systemctl --user show "$NEW_RUN" -p InvocationID --value)" "$(systemctl --user show "$NEW_RUN" -p MainPID --value)"; do
    [ $(( $(date +%s) - t0 )) -ge 60 ] && { log "no pass by the current run within 60 s: rolling back"; rollback; exit 3; }; sleep 5; done
  run systemctl --user start "$NEW_LIVE.service" || { log "outside check failed (its OnFailure handler owns it): rolling back"; rollback; exit 3; }
  if [ "$DRY" != 1 ]; then
    v=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print((d.get("last_verdict") or {}).get("state",""), d.get("last_check_at",""))' "$DB.liveness.json" 2>/dev/null)
    [ "${v%% *}" = rest ] && healthy_eval "$t0" "$v" || { log "outside check not rest after t0 ($v): rolling back"; rollback; exit 3; }
  fi
  run systemctl --user list-timers --all --no-pager
  ok "old owners off and drained; 4 units installed (bytes = release, OnFailure wired); a fresh pass by the current run; outside check rest; one owner"
}

handoff() {
  must "$BIN" dispatch $C --qid P12-production-handoff-1 --worker kiln --verifier corvid --duration 20m --verify-window 10m \
    --task "@$PKG/plans/tasks/handoff-task.md" --verify-task "@$PKG/plans/tasks/handoff-verify.md"
  ok "P12-production-handoff-1 dispatched through agent-loop; Tern decides with: $BIN decide $C --qid P12-production-handoff-1 --kind question_answered --ref <record> --reason <text>"
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
  # the check's OnFailure handler is drained too, AFTER the check (a failing check can still start it)
  drain "$NEW_LIVE.service" "$NEW_FAIL" $(systemctl --user list-units --all --plain --no-legend 'agent-loop-campaign4-*.service' 2>/dev/null | awk '{print $1}')
  for u in "$NEW_RUN" "$NEW_LIVE.timer" "$NEW_LIVE.service" "$NEW_FAIL"; do [ "$DRY" = 1 ] || case "$(systemctl --user is-active "$u" 2>/dev/null)" in active|activating) fail "$u still active: old owners NOT restored";; esac; done
  # 3. open agent-loop packages go to cairn as explicit items (claim paths included); nothing re-sent
  [ "$DRY" = 1 ] || python3 - "$EV/rollback/expose.json" >"$EV/rollback/open-items.json" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
print(json.dumps([p for p in v.get("packages", []) if p.get("step") != "closed"], indent=1))
PY
  # 4. previous binary and old owners back
  [ -e "$PREV" ] && must install -m 755 "$PREV" "$BIN"
  # unit files: the kept originals back; files this cutover added are removed
  for u in $UNITS; do if grep -qx "$u" "$PRE/units-prev.list" 2>/dev/null; then must cp -a "$PRE/units-prev/$u" "$SD/$u"; else run rm -f "$SD/$u"; fi; done
  [ -e "$PRE/config-prev.json" ] && must cp -a "$PRE/config-prev.json" "$CFG"
  must systemctl --user daemon-reload
  # old owners: exactly the captured enabled/active state (state.tsv), nothing more
  [ -s "$PRE/state.tsv" ] || fail "no captured state.tsv: cannot restore the exact prior state"
  while IFS=$'\t' read -r u en ac; do
    if [ "$u" = campaign4-watch.timer ]; then
      [ "$ac" = active ] && must systemd-run --user --unit=campaign4-watch --on-active=45min --on-unit-active=45min $H/.config/agent-deck/campaign4-watch || log "campaign4-watch was $ac at capture: not recreated"
      continue; fi
    [ "$en" = enabled ] && must systemctl --user enable "$u"
    [ "$ac" = active ] && must systemctl --user start "$u"
  done <"$PRE/state.tsv"
  run env AGENTDECK_PROFILE=campaign4 "$H/.config/agent-deck/wake" "$CAIRN_ID" "[P12 cutover $CUT_RUN] ROLLBACK: your controller role is restored. Open agent-loop items to adopt (no resend; check each seat first): $EV/rollback/open-items.json"
  # 5. one owner
  while IFS=$'\t' read -r u en ac; do [ "$DRY" = 1 ] || [ "$u" = campaign4-watch.timer ] || [ "$ac" != active ] || [ "$(systemctl --user is-active "$u")" = active ] || fail "$u not active after rollback (was active at capture)"; done <"$PRE/state.tsv"
  [ "$DRY" = 1 ] || [ "$(systemctl --user is-active "$NEW_RUN")" != active ] || fail "agent-loop still active after rollback"
  ok "rolled back: old owners active, agent-loop off, open items handed to cairn"
}

case "$CMD" in capture) capture;; switch) switch;; handoff) handoff;; rollback) rollback;; *) echo "unknown $CMD" >&2; exit 2;; esac
