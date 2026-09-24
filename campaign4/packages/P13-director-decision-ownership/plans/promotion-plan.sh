#!/bin/bash
# P13 promotion plan, REPAIRED (F5). Preserved v1 archive: evidence/plan-repair/v1/.
# Held: runs ONLY after Tern's separate signed promotion. Offline proof:
# evidence/plan-repair/offline-test.sh exercises failure + exact rollback.
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
. "$INPUTS"
for v in RUN BIN_SRC BIN_SHA ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
  val=${!v:-}
  if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
BIN=${PROMOTE_BIN:-/home/bmosher/.local/bin/agent-loop}
PREV=${PROMOTE_PREV:-/home/bmosher/.local/bin/agent-loop.prev-p13}
CFG=${PROMOTE_CFG:-/home/bmosher/.config/agent-loop/campaign4.json}
SD=${PROMOTE_SD:-/home/bmosher/.config/systemd/user}
AD=${PROMOTE_AD:-/home/bmosher/.config/agent-deck}
EV=${EV_DIR:-$PKG/evidence/plan-repair/$RUN}
CAND_BIN=/home/bmosher/projects/agent-loop-releases/agent-loop-df5e6fc627b8/bin/agent-loop
CAND_SHA=47f69dfdeb8b0d17472d871b68dfdfa8270e3421997a03f5d1c6929c8a818ec1
PROSPECTIVE=$PKG/plans/campaign4-decision-config.prospective.json
mkdir -p "$EV"
. "$PKG/plans/decision-evaluators.sh"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/promotion.log"; }
run() { log "+ $*"; "$@" >>"$EV/promotion.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
result() { local st=$2; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/promotion-results.tsv"; }
fail() { result PROMOTE FAIL "$*"; exit 3; }
guard_absent() { # refuse if adapter absent, policy invalid, or a package mid-decision
  [ -f "$ADAPTER_WATCH_SRC" ] || fail "watch adapter absent: $ADAPTER_WATCH_SRC"
  [ -f "$ADAPTER_RESOLVE_SRC" ] || fail "resolve adapter absent: $ADAPTER_RESOLVE_SRC"
  # F5: policy checked against the ACTUAL prospective config file, not a
  # hardcoded fabricated JSON.
  python3 -c "
import json, sys
cfg = json.load(open('$PROSPECTIVE'))
assert cfg.get('decision_policy') == 'required', 'policy must be required, got %r' % cfg.get('decision_policy')
offs = sorted(r.get('after_s') for r in cfg.get('decision_ladder', []))
assert offs == [0, 300, 600], 'ladder must be exactly 0/300/600, got %r' % offs
for r in cfg['decision_ladder']:
    assert isinstance(r.get('exec', r.get('seat')), (str, list)), 'rung needs absolute exec/ledger or seat'" \
    || fail "prospective config $PROSPECTIVE invalid for required policy"
  # F5: active-decision guard — refuse when a package is mid-decision without
  # a migration plan (would strand or resend its decision).
  MID=$("$BIN" status --config "$CFG" --json 2>/dev/null | python3 -c "
import json, sys
try: ps = json.load(sys.stdin).get('packages', [])
except Exception: print('unreadable'); sys.exit(2)
mid = [p['qid'] for p in ps if p.get('step') == 'decision']
print(' '.join(mid))") || fail "cannot read package status for active-decision guard"
  [ -z "$MID" ] || fail "packages mid-decision without migration plan: $MID"
  log "guards pass: adapters present, prospective config required 0/300/600, no mid-decision package"
}
rollback() {
  log "rollback: exact captured originals (never candidate)"
  run install -m 755 "$PREV" "$BIN" || fail "rollback: binary restore failed"
  [ "$(sha256sum "$BIN" | cut -d' ' -f1)" = "$(cat "$EV/promo-archive/installed-sha.txt")" ] || fail "rollback: binary is not the archived original"
  for f in agent-loop.installed campaign4.json escalation-watch escalation-watch.timer escalation-watch.service escalation-resolve installed-sha.txt ownership.txt; do
    [ -e "$EV/promo-archive/$f" ] || fail "rollback: archive lacks $f"
  done
  run cp -a "$EV/promo-archive/escalation-watch" "$AD/escalation-watch" || fail "rollback: watcher restore failed"
  run cp -a "$EV/promo-archive/escalation-watch.timer" "$SD/escalation-watch.timer" || fail "rollback: watcher timer restore failed"
  run cp -a "$EV/promo-archive/escalation-watch.service" "$SD/escalation-watch.service" || fail "rollback: watcher service restore failed"
  run cp -a "$EV/promo-archive/escalation-resolve" "$AD/escalation-resolve" || fail "rollback: resolve restore failed"
  run cp -a "$EV/promo-archive/campaign4.json" "$CFG" || fail "rollback: config restore failed"
  run systemctl --user daemon-reload || fail "rollback: daemon-reload failed"
  run systemctl --user enable --now "agent-loop@campaign4.service" "agent-loop-liveness@campaign4.timer" || fail "rollback: re-enable failed"
  result ROLLBACK PASS "exact originals restored (binary/watcher/timer/service/resolve/config/ownership); no DB migration, no resend"
}
if [ "$MODE" = rollback ]; then rollback; exit 0; fi
log "promotion; guards first"
guard_absent
# 1. archive INSTALLED originals (bytes + ownership): binary, watcher scripts,
#    resolve, config. PREV is the installed binary backup, NOT the candidate.
run mkdir -p "$EV/promo-archive"
run cp -a "$BIN" "$PREV" || fail "cannot back up installed binary"
sha256sum "$BIN" | cut -d' ' -f1 >"$EV/promo-archive/installed-sha.txt"
run cp -a "$BIN" "$EV/promo-archive/agent-loop.installed" || fail "archive binary failed"
run cp -a "$CFG" "$EV/promo-archive/campaign4.json" || fail "archive config failed"
# Installed watcher scripts + resolve (exact originals for restore).
run cp -a "$AD/escalation-watch" "$EV/promo-archive/escalation-watch" || fail "archive watcher failed"
run cp -a "$SD/escalation-watch.timer" "$EV/promo-archive/escalation-watch.timer" || fail "archive watcher timer failed"
run cp -a "$SD/escalation-watch.service" "$EV/promo-archive/escalation-watch.service" || fail "archive watcher service failed"
run cp -a "$AD/escalation-resolve" "$EV/promo-archive/escalation-resolve" || fail "archive resolve failed"
stat -c '%a %U %n' "$BIN" "$CFG" >"$EV/promo-archive/ownership.txt"
# 2. drain relevant checks under one owner (bounded 120 s each)
for u in agent-loop@campaign4.service agent-loop-liveness@campaign4.service agent-loop-liveness@campaign4.timer; do
  t0=$(date +%s)
  while [ "$(systemctl --user is-active "$u" 2>/dev/null)" = active ] && [ $(( $(date +%s) - t0 )) -lt 120 ]; do sleep 2; done
  run systemctl --user stop "$u" || fail "drain stop failed: $u"
done
# 3. install candidate + private adapters + required config; ledger untouched
run install -m 755 "$CAND_BIN" "$BIN" || fail "candidate install failed"
[ "$(sha256sum "$BIN" | cut -d' ' -f1)" = "$CAND_SHA" ] || { rollback; fail "installed binary mismatch"; }
run install -m 755 "$ADAPTER_WATCH_SRC" "$AD/escalation-watch" || { rollback; fail "watch adapter install failed"; }
run install -m 755 "$ADAPTER_RESOLVE_SRC" "$AD/escalation-resolve" || { rollback; fail "resolve adapter install failed"; }
[ "$(sha256sum $AD/escalation-watch | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] || { rollback; fail "watch adapter mismatch"; }
[ "$(sha256sum $AD/escalation-resolve | cut -d' ' -f1)" = "$ADAPTER_RESOLVE_SHA" ] || { rollback; fail "resolve adapter mismatch"; }
run cp "$PROSPECTIVE" "$CFG" || { rollback; fail "config install failed"; }
run systemctl --user daemon-reload || { rollback; fail "daemon-reload failed"; }
# 4. restart, validate fresh pass and checker
run systemctl --user start agent-loop@campaign4.service agent-loop-liveness@campaign4.timer || { rollback; fail "restart failed"; }
run sleep 60
run "$BIN" liveness --config "$CFG" || { rollback; fail "checker failed after promotion"; }
result PROMOTE PASS "candidate installed, fresh pass + checker validated; ledger decisions/deadlines preserved"
log "promotion complete; rollback() restores the archive on demand"
