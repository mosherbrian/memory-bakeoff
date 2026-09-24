#!/bin/bash
# P13 stand-in offline rehearsal: DRY runs + negative assertions. No live
# fixture launches, no service changes/reloads, no real wakes/Signal, no
# shared ledger writes. Stubs live in a private temporary HOME only.
# Any failed command fails the overall stage (set -e + explicit asserts).
set -uo pipefail
set +o pipefail  # evaluator FAIL paths exit nonzero by design; greps below judge output, not pipe status
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
PLANS=$PKG/plans
EV=$PKG/evidence/plan-standin/rehearsal-1
rm -rf "$EV"; mkdir -p "$EV"
TMP=$(mktemp -d /tmp/p13rehearse-XXXXXX)
export HOME="$TMP/home"; mkdir -p "$HOME"
export PATH="$TMP/bin:/usr/bin:/bin"
mkdir -p "$TMP/bin"
# Stub firewall: if DRY ever tries to execute these, fail loudly.
for c in systemctl systemd-run agent-deck journalctl; do
  printf '#!/bin/bash\necho "STUB-LEAK: %s $*" >&2; exit 99\n' "$c" > "$TMP/bin/$c"
  chmod +x "$TMP/bin/$c"
done
pass=0; fail=0
ok() { pass=$((pass+1)); echo "PASS $1" | tee -a "$EV/rehearsal.log"; }
no() { fail=$((fail+1)); echo "FAIL $1" | tee -a "$EV/rehearsal.log"; }
# Shared-state sentinels: production ledger, wake log, shared escalation ledger.
SLEDGER=/home/bmosher/.local/share/agent-loop/campaign4.db
WAKELOG=/home/bmosher/.local/share/agent-deck/wake-send.log
ESCLEDGER=/home/bmosher/.local/share/agent-deck/escalations.jsonl
snap_shared() { sha256sum "$SLEDGER" 2>/dev/null; wc -l <"$WAKELOG" 2>/dev/null; wc -l <"$ESCLEDGER" 2>/dev/null; }
BEFORE=$(snap_shared)

# 1. Filled rehearsal inputs (late-bound fields enumerated, fixture values).
sed -e "s#<run-id, e.g. p13d1>#r1#" -e "s#<private root, e.g. /tmp/p13d1-root>#$TMP/root#" \
  -e "s#<UTC, e.g. 2026-09-24T07:00:00Z>#2030-01-01T00:10:00Z#" \
  -e "s#<agent-deck profile for fixture seats>#campaign4#" \
  -e "s#<fixture wake stub path (private ROOT/bin/wake); never the shared wake>#$TMP/root/bin/wake#" \
  -e "s#<private stream dir>#$TMP/root/streams#" \
  -e "s#<fixture worker title>#fx-w#" -e "s#<fixture worker session id>#fx-w-id#" \
  -e "s#<fixture verifier title>#fx-v#" -e "s#<fixture verifier session id>#fx-v-id#" \
  -e "s#<fixture director title>#fx-d#" -e "s#<fixture director session id>#fx-d-id#" \
  -e "s#<fixture duty title>#fx-u#" -e "s#<fixture duty session id>#fx-u-id#" \
  -e "s#<private ROOT>/escalations.jsonl#$TMP/root/escalations.jsonl#" \
  -e "s#<private ROOT>/bin/notify-claude#$TMP/root/bin/notify-claude#" \
  -e "s#<private ROOT>/bin/escalation-resolve#$TMP/root/bin/escalation-resolve#" \
  -e "s#<private ROOT>/ticket-stub.log#$TMP/root/ticket-stub.log#" \
  "$PLANS/live-inputs.template.env" > "$EV/inputs-filled.env"
grep -v "^#" "$EV/inputs-filled.env" | grep -q "<" && no "inputs still have unfilled fields" || ok "inputs fully late-bound"

# 2. DRY live20 run (rehearsal).
EV_DIR="$EV/live" DRY=1 bash "$PLANS/live20-plan.sh" "$EV/inputs-filled.env" run >"$EV/live20-dry.log" 2>&1
[ $? -eq 0 ] && ok "live20 DRY rc0" || no "live20 DRY rc=$?"
grep -q "STUB-LEAK" "$EV/live20-dry.log" "$EV/live/driver.log" 2>/dev/null && no "DRY executed a stubbed host command" || ok "DRY executed nothing host-side"
[ -f "$EV/live/driver.log" ] && ok "driver log exists" || no "driver log missing"
grep -q $'\tFAIL\t' "$EV/live/results.tsv" 2>/dev/null && no "DRY recorded FAIL" || ok "no FAIL rows in DRY"

# 3. DRY promotion run.
EV_DIR="$EV/promo" DRY=1 bash "$PLANS/promotion-plan.sh" "$EV/inputs-filled.env" run >"$EV/promo-dry.log" 2>&1
[ $? -eq 0 ] && ok "promotion DRY rc0" || no "promotion DRY rc=$?"
grep -q "STUB-LEAK" "$EV/promo-dry.log" 2>/dev/null && no "promotion DRY executed stub" || ok "promotion DRY clean"

# 4. Negative assertions.
DRY=1 bash "$PLANS/live20-plan.sh" "$PLANS/live-inputs.template.env" run >/dev/null 2>&1
[ $? -eq 2 ] && ok "unfilled template refused rc2" || no "unfilled template rc=$?"
bash "$PLANS/live20-plan.sh" >/dev/null 2>&1
[ $? -ne 0 ] && ok "missing arg refused" || no "missing arg accepted"
echo '{"decision_policy":"required","decision_ladder":[{"after_s":0},{"after_s":300},{"after_s":600}],"decision_deadline_s":1800}' | bash -c '. "$0"; policy_eval' "$PLANS/decision-evaluators.sh" | grep -q ^PASS && ok "required 0/300/600 passes offline" || no "required policy rejected"
echo '{"decision_policy":"required","decision_ladder":[{"after_s":0},{"after_s":300}],"decision_deadline_s":1800}' | bash -c '. "$0"; policy_eval' "$PLANS/decision-evaluators.sh" | grep -q ^FAIL && ok "malformed required ladder fails" || no "malformed ladder accepted"
echo '{"decision_policy":"weird"}' | bash -c '. "$0"; policy_eval' "$PLANS/decision-evaluators.sh" | grep -q ^FAIL && ok "unknown policy fails" || no "unknown policy accepted"
echo '{"decision_policy":"generic","decision_ladder":[{"after_s":0},{"after_s":20},{"after_s":40}],"decision_deadline_s":60}' | bash -c '. "$0"; policy_eval' "$PLANS/decision-evaluators.sh" | grep -q ^PASS && ok "generic 0/20/40+60 passes (fixture deviation declared)" || no "generic policy rejected"
printf 'rung:director\nrung:duty\nrung:claude\n' | bash -c '. "$0"; rung_order_eval director,duty,claude' "$PLANS/decision-evaluators.sh" | grep -q ^PASS && ok "rung order evaluator" || no "rung order"
printf 'rung:duty\nrung:director\n' | bash -c '. "$0"; rung_order_eval director,duty,claude' "$PLANS/decision-evaluators.sh" | grep -q ^FAIL && ok "rung disorder fails" || no "rung disorder accepted"
bash -c '. "$0"; recur_eval K K' "$PLANS/decision-evaluators.sh" | grep -q ^PASS && ok "same-key recurrence" || no "recurrence"
bash -c '. "$0"; recur_eval K J' "$PLANS/decision-evaluators.sh" | grep -q ^FAIL && ok "key-change recurrence fails" || no "key change accepted"
NOW=$(date +%s); VD=$((NOW+600))
printf '{"incident":"Q1","responder":"fx-u","next_action":"page duty","response_deadline":%d}' "$VD" > "$TMP/ack.json"
bash -c '. "$0"; ack_eval "$1" Q1 fx-u' "$PLANS/decision-evaluators.sh" "$TMP/ack.json" | grep -q ^PASS && ok "valid ack passes" || no "valid ack rejected"
printf '{"incident":"Q1","responder":"literal-claude","next_action":"x","response_deadline":%d}' "$VD" > "$TMP/ack-bad.json"
bash -c '. "$0"; ack_eval "$1" Q1 fx-u' "$PLANS/decision-evaluators.sh" "$TMP/ack-bad.json" | grep -q ^FAIL && ok "wrong-responder ack fails" || no "wrong responder accepted"
printf '{"incident":"Q1","responder":"fx-u","next_action":"x","response_deadline":%d}' "$((NOW+9999))" > "$TMP/ack-late.json"
bash -c '. "$0"; ack_eval "$1" Q1 fx-u' "$PLANS/decision-evaluators.sh" "$TMP/ack-late.json" | grep -q ^FAIL && ok "over-15min deadline fails" || no "forged deadline accepted"
printf 'decide Q1\n' > "$TMP/ledger.txt"
bash -c '. "$0"; suppress_eval Q1' "$PLANS/decision-evaluators.sh" <"$TMP/ledger.txt" | grep -q ^PASS && ok "suppression check" || no "suppression"
printf 'page Q1\n' >> "$TMP/ledger.txt"
bash -c '. "$0"; suppress_eval Q1' "$PLANS/decision-evaluators.sh" <"$TMP/ledger.txt" | grep -q ^FAIL && ok "post-decide page fails" || no "page after decide accepted"
printf 'send Q1\nrepeat Q1 ambiguous\n' > "$TMP/sends.txt"
bash -c '. "$0"; nodup_eval Q1 "$1"' "$PLANS/decision-evaluators.sh" "$TMP/sends.txt" | grep -q ^PASS && ok "one labelled repeat ok" || no "repeat bound"
printf 'repeat Q1\nrepeat Q1\n' >> "$TMP/sends.txt"
bash -c '. "$0"; nodup_eval Q1 "$1"' "$PLANS/decision-evaluators.sh" "$TMP/sends.txt" | grep -q ^FAIL && ok "two repeats fail" || no "double repeat accepted"

# 5. No shared writes, no secret logging, no caller-default leaks.
AFTER=$(snap_shared)
[ "$BEFORE" = "$AFTER" ] && ok "shared ledger/wake/escalation untouched" || no "shared state changed: $BEFORE -> $AFTER"
grep -rq "notify-claude decision" "$TMP/root" 2>/dev/null && no "real notify path touched" || ok "no real notify path touched"
grep -rqiE "cap[^a-z].{0,20}[0-9a-f]{32,}|secret|BEGIN.*PRIVATE" "$EV" 2>/dev/null && no "secret material in evidence" || ok "no secret material in evidence"
grep -q "STUB-LEAK" "$EV/live/driver.log" 2>/dev/null && no "leaked host exec in driver log" || ok "driver log has no leaked exec"
grep -q "/home/bmosher/.local/share/agent-loop/campaign4.db\|/home/bmosher/.local/share/agent-deck/wake-send.log\|/home/bmosher/.local/share/agent-deck/escalations.jsonl" "$EV/live/driver.log" 2>/dev/null && no "shared paths in driver log" || ok "no shared paths referenced"

echo "rehearsal: $pass passed, $fail failed" | tee -a "$EV/rehearsal.log"
[ "$fail" -eq 0 ]
