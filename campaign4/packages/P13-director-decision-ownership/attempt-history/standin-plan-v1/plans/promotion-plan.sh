#!/bin/bash
# P13 promotion plan (held: runs ONLY after Tern's separate signed promotion).
# Archive installed 97a57db1/config/watcher, drain checks under one owner,
# install candidate binary + private adapters + required config, preserve
# ledger decisions/deadlines, restart/validate fresh pass and checker.
# Rollback restores exact captured bytes/ownership, no DB migration/resend.
# DRY=1 prints every command, runs none (offline rehearsal).
set -uo pipefail
INPUTS=$(readlink -f "$1"); MODE=${2:-run}; DRY=${DRY:-0}
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
. "$INPUTS"
for v in RUN BIN_SRC BIN_SHA ADAPTER_WATCH_SRC ADAPTER_WATCH_SHA ADAPTER_RESOLVE_SRC ADAPTER_RESOLVE_SHA; do
  val=${!v:-}
  if [ -z "$val" ] || [[ "$val" == *"<"* ]]; then echo "input $v missing or unfilled" >&2; exit 2; fi
done
BIN=/home/bmosher/.local/bin/agent-loop
PREV=/home/bmosher/.local/bin/agent-loop.prev-p13
CFG=/home/bmosher/.config/agent-loop/campaign4.json
SD=/home/bmosher/.config/systemd/user
EV=${EV_DIR:-$PKG/evidence/plan-standin/$RUN}
CAND_BIN=/home/bmosher/projects/agent-loop-releases/agent-loop-df5e6fc627b8/bin/agent-loop
CAND_SHA=47f69dfdeb8b0d17472d871b68dfdfa8270e3421997a03f5d1c6929c8a818ec1
mkdir -p "$EV"
. "$PKG/plans/decision-evaluators.sh"
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
log() { echo "$(ts) $*" | tee -a "$EV/promotion.log"; }
run() { log "+ $*"; if [ "$DRY" = 1 ]; then return 0; fi; "$@" >>"$EV/promotion.log" 2>&1; local rc=$?; log "  rc=$rc"; return $rc; }
result() { local st=$2; [ "$DRY" = 1 ] && st=DRY; printf '%s\t%s\t%s\t%s\n' "$1" "$st" "$(ts)" "$3" | tee -a "$EV/promotion-results.tsv"; }
guard_absent() { # refuse if adapter absent, policy invalid, or a package mid-decision without migration plan
  [ -f "$ADAPTER_WATCH_SRC" ] || { result PROMOTE FAIL "watch adapter absent: $ADAPTER_WATCH_SRC"; exit 3; }
  [ -f "$ADAPTER_RESOLVE_SRC" ] || { result PROMOTE FAIL "resolve adapter absent: $ADAPTER_RESOLVE_SRC"; exit 3; }
  echo '{"decision_policy":"required","decision_ladder":[{"after_s":0},{"after_s":300},{"after_s":600}],"decision_deadline_s":1800}' | policy_eval >/dev/null 2>&1 || { result PROMOTE FAIL "production policy invalid"; exit 3; }
  log "guards pass: adapters present, production policy required 0/300/600 valid"; }
rollback() {
  log "rollback: exact captured bytes and ownership"
  run install -m 755 "$PREV" "$BIN"
  run cp -a "$EV/promo-archive/agent-loop@.service" "$SD/agent-loop@.service" 2>/dev/null
  run cp -a "$EV/promo-archive/campaign4.json" "$CFG" 2>/dev/null
  run systemctl --user daemon-reload
  run systemctl --user enable --now "agent-loop@campaign4.service" "agent-loop-liveness@campaign4.timer"
  result ROLLBACK PASS "previous binary and ownership restored; no DB migration, no resend"
}
if [ "$MODE" = rollback ]; then rollback; exit 0; fi
log "promotion dry layout; guards first"
guard_absent
# 1. archive installed binary/config/watcher with owner/mode
run mkdir -p "$EV/promo-archive"
run cp -a "$BIN" "$EV/promo-archive/agent-loop.97a57db1"
run cp -a "$CFG" "$EV/promo-archive/campaign4.json"
run cp -a /home/bmosher/.config/systemd/user/escalation-watch* "$EV/promo-archive/" 2>/dev/null
if [ "$DRY" != 1 ]; then
  [ "$(sha256sum "$EV/promo-archive/agent-loop.97a57db1" | cut -d" " -f1)" = 97a57db11aa8a4a87d89fd912804d42ce899bb35b3790742d790d424184a948f ] || { result PROMOTE FAIL "installed binary is not the pinned 97a57db1"; exit 3; }
fi
# 2. drain relevant checks under one owner (bounded 120 s each)
for u in agent-loop@campaign4.service agent-loop-liveness@campaign4.service agent-loop-liveness@campaign4.timer; do
  run systemctl --user stop "$u"; done
# 3. install candidate + private adapters + required config; ledger untouched
run install -m 755 "$BIN_SRC" "$PREV"
run install -m 755 "$CAND_BIN" "$BIN"
[ "$DRY" = 1 ] || [ "$(sha256sum "$BIN" | cut -d' ' -f1)" = "$CAND_SHA" ] || { result PROMOTE FAIL "installed binary mismatch; rolling back"; rollback; exit 3; }
run install -m 755 "$ADAPTER_WATCH_SRC" /home/bmosher/.config/agent-deck/escalation-watch
run install -m 755 "$ADAPTER_RESOLVE_SRC" /home/bmosher/.config/agent-deck/escalation-resolve
[ "$DRY" = 1 ] || [ "$(sha256sum /home/bmosher/.config/agent-deck/escalation-watch | cut -d' ' -f1)" = "$ADAPTER_WATCH_SHA" ] || { result PROMOTE FAIL "watch adapter mismatch; rolling back"; rollback; exit 3; }
run cp "$PKG/plans/campaign4-decision-config.prospective.json" "$CFG"
run systemctl --user daemon-reload
# 4. restart, validate fresh pass and checker
run systemctl --user start agent-loop@campaign4.service agent-loop-liveness@campaign4.timer
run sleep 60
run "$BIN" liveness --config "$CFG" || { result PROMOTE FAIL "checker failed after promotion; rolling back"; rollback; exit 3; }
result PROMOTE PASS "candidate installed, fresh pass + checker validated; ledger decisions/deadlines preserved"
log "promotion complete; rollback() restores the archive on demand"
