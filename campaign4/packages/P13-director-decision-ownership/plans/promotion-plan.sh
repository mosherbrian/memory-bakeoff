#!/bin/bash
# P13 promotion plan v2 (P13-promotion-closure-1). Runs ONLY after Tern's signed promotion. Previous version:
# attempt-history/pre-promotion-closure/promotion-plan.sh. Sandbox proof: evidence/promotion-closure/sandbox-test.sh.
# Order: guards (no mutation) -> snapshot presence/absence + hash + mode + unit active/enabled -> stop timers
# first, then services (bounded; never wait for a running loop to stop itself) -> install exact pins -> start
# what was active -> verify: new run invocation + a fresh ledger pass by it + a healthy checker verdict after
# the start + required 0/300/600 policy. Any failure after the first mutation -> exact restore (absent files are
# removed, never fabricated; unit states back to the snapshot) -> PROMOTE FAIL. Bound: 10 min.
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
. "$INPUTS"
for v in RUN ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
  val=${!v:-}; if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi; done
SANDBOX=${PROMOTE_SANDBOX:-0}   # 1 only in the sandbox test; labelled on every result row
if [ "$SANDBOX" = 1 ]; then R=${PROMOTE_ROOT:?}; else R=; fi
BIN=$R/home/bmosher/.local/bin/agent-loop
CFG=$R/home/bmosher/.config/agent-loop/campaign4.json
AD=$R/home/bmosher/.config/agent-deck
SC=${PROMOTE_SYSTEMCTL:-systemctl}; [ "$SANDBOX" = 1 ] || SC=systemctl
EV=${PROMOTE_EV:-$PKG/evidence/promotion-$RUN}; ARC=$EV/promo-archive
CAND_BIN=/home/bmosher/projects/agent-loop-releases/agent-loop-df5e6fc627b8/bin/agent-loop
CAND_SHA=47f69dfdeb8b0d17472d871b68dfdfa8270e3421997a03f5d1c6929c8a818ec1
PROSPECTIVE=$PKG/plans/campaign4-decision-config.prospective.json
TIMERS="agent-loop-liveness@campaign4.timer escalation-watch.timer"
SERVICES="agent-loop@campaign4.service agent-loop-liveness@campaign4.service agent-loop-liveness-failed@campaign4.service escalation-watch.service"
FILES="$BIN $CFG $AD/escalation-watch $AD/escalation-resolve"
T0=$(date +%s); BOUND=600
mkdir -p "$EV"
. "$PKG/../P12-timeout-ownership-live-closure/plans/live-checks.sh"   # pass_eval, healthy_eval (pinned, tested)
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/promotion.log"; }
run() { log "+ $*"; "$@" >>"$EV/promotion.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
result() { local st=$2; [ "$SANDBOX" = 1 ] && st="SANDBOX-$st"; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/promotion-results.tsv"; }
MUTATED=0
fail() { if [ "$MUTATED" = 1 ]; then restore; fi; result PROMOTE FAIL "$*"; exit 3; }
in_time() { [ $(( $(date +%s) - T0 )) -lt $BOUND ] || fail "promotion bound ${BOUND}s exceeded"; }
# ---- guards: NO mutation
guards() {
  [ "$(sha256sum "$CAND_BIN" | cut -d' ' -f1)" = "$CAND_SHA" ] || fail "candidate binary hash"
  [ "$(sha256sum "$ADAPTER_WATCH_SRC" | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] || fail "watch adapter hash"
  [ "$(sha256sum "$ADAPTER_RESOLVE_SRC" | cut -d' ' -f1)" = "$ADAPTER_RESOLVE_SHA" ] || fail "resolve adapter hash"
  "$CAND_BIN" status --config "$PROSPECTIVE" >/dev/null 2>>"$EV/promotion.log" || fail "prospective config refused by the candidate (required 0/300/600 policy)"
  MID=$("$BIN" status --config "$CFG" --json 2>/dev/null | python3 -c "
import json, sys
try: ps = json.load(sys.stdin).get('packages', [])
except Exception: print('unreadable'); sys.exit(2)
print(' '.join(p['qid'] for p in ps if p.get('step') == 'decision'))") || fail "package status unreadable"
  [ -z "$MID" ] || fail "packages mid-decision: $MID"
  log "guards pass (no mutation)"; }
# ---- snapshot: presence/absence, bytes, hash, mode; unit active/enabled
snapshot() {
  mkdir -p "$ARC"; : > "$ARC/files.tsv"; : > "$ARC/units.tsv"
  local i=0 f
  for f in $FILES; do i=$((i+1))
    if [ -e "$f" ]; then cp -p "$f" "$ARC/f$i"; printf '%s\tpresent\t%s\t%s\tf%d\n' "$f" "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %a "$f")" $i >> "$ARC/files.tsv"
    else printf '%s\tabsent\t-\t-\t-\n' "$f" >> "$ARC/files.tsv"; fi; done
  for u in $TIMERS $SERVICES; do printf '%s\t%s\t%s\n' "$u" "$($SC --user is-active "$u" 2>/dev/null)" "$($SC --user is-enabled "$u" 2>/dev/null)" >> "$ARC/units.tsv"; done
  OLD_INV=$($SC --user show agent-loop@campaign4.service -p InvocationID --value 2>/dev/null)
  log "snapshot: $(cut -f1,2 "$ARC/files.tsv" | tr '\t\n' ': ') units $(cut -f1,2,3 "$ARC/units.tsv" | tr '\t\n' ':;')"; }
restore() {
  log "RESTORE to the snapshot"
  local u st en
  for u in $TIMERS $SERVICES; do $SC --user stop "$u" >>"$EV/promotion.log" 2>&1; done
  while IFS=$'\t' read -r f pres sha mode key; do
    if [ "$pres" = present ]; then cp -p "$ARC/$key" "$f" && [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$sha" ] || log "RESTORE MISMATCH $f"
    else rm -f "$f"; [ ! -e "$f" ] || log "RESTORE could not remove introduced $f"; fi
  done < "$ARC/files.tsv"
  $SC --user daemon-reload >>"$EV/promotion.log" 2>&1
  while IFS=$'\t' read -r u st en; do
    [ "$st" = active ] && $SC --user start "$u" >>"$EV/promotion.log" 2>&1
  done < "$ARC/units.tsv"
  local bad=0
  while IFS=$'\t' read -r f pres sha mode key; do
    if [ "$pres" = present ]; then [ "$(sha256sum "$f" 2>/dev/null | cut -d' ' -f1)" = "$sha" ] && [ "$(stat -c %a "$f")" = "$mode" ] || bad=1; else [ ! -e "$f" ] || bad=1; fi
  done < "$ARC/files.tsv"
  while IFS=$'\t' read -r u st en; do [ "$($SC --user is-active "$u" 2>/dev/null)" = "$st" ] || bad=1; done < "$ARC/units.tsv"
  [ $bad = 0 ] && result ROLLBACK PASS "files and unit states equal the snapshot (absent files absent)" || result ROLLBACK FAIL "state differs from the snapshot after restore"; }
[ "$MODE" = rollback ] && { MUTATED=0; restore; exit 0; }
log "promotion $RUN"; guards; snapshot
# ---- stop timers first, then services; bounded; never wait for the loop to stop itself
MUTATED=1
for u in $TIMERS $SERVICES; do in_time; timeout 30 $SC --user stop "$u" >>"$EV/promotion.log" 2>&1 || fail "stop $u"; done
for u in $TIMERS $SERVICES; do [ "$($SC --user is-active "$u" 2>/dev/null)" != active ] || fail "$u still active after stop"; done
# ---- install exact pins
run install -m 755 "$CAND_BIN" "$BIN" || fail "binary install"
run install -m 755 "$ADAPTER_WATCH_SRC" "$AD/escalation-watch" || fail "watch adapter install"
run install -m 755 "$ADAPTER_RESOLVE_SRC" "$AD/escalation-resolve" || fail "resolve adapter install"
run install -m 644 "$PROSPECTIVE" "$CFG" || fail "config install"
[ "$(sha256sum "$BIN" | cut -d' ' -f1)" = "$CAND_SHA" ] && [ "$(sha256sum "$AD/escalation-watch" | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] \
  && [ "$(sha256sum "$AD/escalation-resolve" | cut -d' ' -f1)" = "$ADAPTER_RESOLVE_SHA" ] && cmp -s "$PROSPECTIVE" "$CFG" || fail "installed bytes differ from pins"
run $SC --user daemon-reload || fail "daemon-reload"
# ---- start what the snapshot had active (the intended ownership), then verify freshly
T1=$(date +%s)
while IFS=$'\t' read -r u st en; do [ "$st" = active ] && { run $SC --user start "$u" || fail "start $u"; }; done < "$ARC/units.tsv"
NEW_INV=""; for i in $(seq 1 30); do in_time; NEW_INV=$($SC --user show agent-loop@campaign4.service -p InvocationID --value 2>/dev/null); [ -n "$NEW_INV" ] && [ "$NEW_INV" != "$OLD_INV" ] && break; sleep 2; done
[ -n "$NEW_INV" ] && [ "$NEW_INV" != "$OLD_INV" ] || fail "no new run invocation"
DB=$(python3 -c "import json; print(json.load(open('$CFG'))['db'].replace('~', '$R/home/bmosher', 1))")
pass_ok() { python3 -c 'import sqlite3,sys; c=sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True, timeout=1); print(c.execute("select value from driver_kv where key=?", ("loop-pass",)).fetchone()[0])' "$DB" 2>/dev/null \
  | pass_eval "$T1" "$NEW_INV" "$($SC --user show agent-loop@campaign4.service -p MainPID --value)"; }
ok=0; for i in $(seq 1 45); do in_time; pass_ok && { ok=1; break; }; sleep 2; done
[ $ok = 1 ] || fail "no fresh ledger pass by the new invocation $NEW_INV"
run "$BIN" liveness --config "$CFG" || fail "checker run failed"
v=$(python3 -c "import json; d=json.load(open('$DB.liveness.json')); print((d.get('last_verdict') or {}).get('state',''), d.get('last_check_at',''))" 2>/dev/null)
healthy_eval "$T1" "$v" || fail "checker verdict not healthy after the start: $v"
"$BIN" status --config "$CFG" >/dev/null 2>&1 || fail "installed config refused"
MUTATED=0
result PROMOTE PASS "pins installed; new invocation $NEW_INV with a fresh pass; checker healthy ($v); required policy loaded; ledger untouched"
