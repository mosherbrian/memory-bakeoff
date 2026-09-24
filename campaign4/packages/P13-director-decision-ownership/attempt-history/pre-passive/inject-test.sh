#!/bin/bash
# P13-live-composition-1: run the EXACT live branch (plans/live-p13-driver.sh, not DRY) with injected
# OS/transport collaborators (systemctl, systemd-run, journalctl, agent-deck, ss, curl on PATH; private
# HOME and unit dir; a seat-runtime double on the real wake's sockets). The REAL wake, REAL notify-claude,
# REAL escalations, candidate binary and private adapters run unchanged. Every row is INJECTED-*: this is
# NOT live proof. Then anti-stub negatives for live mode. Usage: inject-test.sh DEADLINE_UTC
set -uo pipefail
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
H=$PKG/evidence/live-composition; EV=$H/run${2:+-$2}; rm -rf "$EV"; mkdir -p "$EV"
DL=$1; MODE=${2:-positive}; left=$(( $(date -u -d "$DL" +%s) - $(date +%s) )); [ "$left" -ge ${MIN_LEFT:-600} ] || { echo "REFUSED: ${left}s left"; exit 3; }
export INJ=$(mktemp -d /tmp/p13inj-XXXXXX); REALHOME=$HOME
export HOME=$INJ/home STREAMS=$INJ/streams INJECT=1 INJECT_SD=$INJ/sd; mkdir -p "$HOME/.local/share/agent-deck" "$INJECT_SD" "$STREAMS"
export PATH="$H/stubs:/usr/bin:/bin"
pass=0; fail=0; ok() { pass=$((pass+1)); echo "PASS $1" | tee -a "$EV/test.log"; }; no() { fail=$((fail+1)); echo "FAIL $1" | tee -a "$EV/test.log"; }
R=inj$(date +%H%M%S); W=$R-w-id V=$R-v-id D=$R-d-id U=$R-u-id
python3 -c "import json,sys; json.dump([{'id': i, 'title': t, 'profile': 'campaign4', 'status': 'idle'} for i, t in zip(sys.argv[1::2], sys.argv[2::2])], open('$INJ/registry.json','w'))" $W fx-w-$R $V fx-v-$R $D fx-d-$R $U fx-u-$R
case "$MODE" in
  neg-early-decide) export SEAT_DIRECTOR_DECIDES=1;; neg-missing-priming) export SEAT_PRIMING=missing;;
  neg-wrong-priming) export SEAT_PRIMING=wrong;; queued) export SEAT_QUEUED=1;; positive) ;; *) echo "unknown mode $MODE"; exit 2;; esac
python3 "$H/seat-runtime.py" $W $V $D $U & SEATPID=$!
sleep 1
SHW=/var/home/bmosher/.local/share/agent-deck/wake-send.log; SHE=/var/home/bmosher/.local/share/agent-deck/escalations.jsonl
W0=$(wc -l <"$SHW"); E0=$(wc -l <"$SHE")
sed -e "s#<fresh run id, e.g. p13l1>#$R#" -e "s#<absolute private root, e.g. /home/bmosher/p13live-RUN; must not exist>#$INJ/root#" \
    -e "s#<absolute UTC end of the signed live20 grant>#$DL#" -e "s#^STREAMS=.*#STREAMS=$STREAMS#" \
    -e "s#^W_NAME=.*#W_NAME=fx-w-$R#" -e "s#^W_ID=.*#W_ID=$W#" -e "s#^V_NAME=.*#V_NAME=fx-v-$R#" -e "s#^V_ID=.*#V_ID=$V#" \
    -e "s#^D_NAME=.*#D_NAME=fx-d-$R#" -e "s#^D_ID=.*#D_ID=$D#" -e "s#^U_NAME=.*#U_NAME=fx-u-$R#" -e "s#^U_ID=.*#U_ID=$U#" \
    "$PKG/plans/live-p13-inputs.template.env" > "$EV/inputs.env"
grep -v '^#' "$EV/inputs.env" | grep -q '<' && no "inputs unfilled" || ok "inputs late-bound"
EV_DIR=$EV/driver bash "$PKG/plans/live-p13-driver.sh" "$EV/inputs.env" run > "$EV/driver.out" 2>&1; DRC=$?
if [ "${MODE#neg-}" != "$MODE" ]; then
  want=PRECONDITION; [ "$MODE" = neg-early-decide ] || want=INDUCTION
  [ $DRC -eq 4 ] && grep -q "^$want	INJECTED-INVALID" "$EV/driver/results.tsv" && ! grep -q "^LIVE	" "$EV/driver/results.tsv" && ! grep -q "^DECISION	" <([ "$want" = INDUCTION ] && cat "$EV/driver/results.tsv") && ok "NEG $MODE -> $want INVALID, rc 4, no LIVE row" || no "NEG $MODE not classified $want INVALID (rc $DRC)"
  case "$MODE" in neg-early-decide) grep -q "EARLY-DECIDE" "$INJ/seat-runtime.log" && ok "NEG the injected director really decided early" || no "NEG director double did not decide";;
    *) pm=${MODE#neg-}; pm=${pm%-priming}; grep -q "PRIMING .* mode=$pm" "$INJ/seat-runtime.log" && ! grep -q "dispatch --config" "$EV/driver/driver.log" && ok "NEG priming ${MODE#neg-}: no dispatch happened" || no "NEG priming case dispatched or not exercised";; esac
  python3 -c "import json; assert not json.load(open('$INJ/registry.json'))" && ok "NEG fixtures removed after INVALID" || no "NEG fixtures remain"
  kill $SEATPID 2>/dev/null; for p in $(ps -eo pid,args | grep -F "$INJ" | grep -v -e "grep -F" | awk '{print $1}'); do kill "$p" 2>/dev/null; done
  echo "inject-test($MODE): $pass passed, $fail failed (INJECTED)" | tee -a "$EV/test.log"; [ $fail -eq 0 ]; exit
fi
[ $DRC -eq 0 ] && ok "live branch rc 0 (injected)" || no "live branch rc $DRC"
grep -q "^INDUCTION	INJECTED-PASS" "$EV/driver/results.tsv" && [ "$(grep -c "PRIMING .* mode=ok" "$INJ/seat-runtime.log")" = 2 ] && ok "induction: both fixtures confirmed exact nonces before dispatch" || no "no confirmed induction"
[ "$MODE" = queued ] && { grep -qP "\tqueued" "$HOME/.local/share/agent-deck/wake-send.log" && ok "queued receipts (wake rc 3) accepted for director/duty rungs" || no "queued not exercised"; }
grep -q "DECISION OVERDUE" <(awk -F'\t' -v d="$D" '$4==d' "$HOME/.local/share/agent-deck/wake-send.log") && ok "incident-bound director rung in transport" || no "no incident-bound director transport"
grep -q "^LIVE	INJECTED-PASS" "$EV/driver/results.tsv" 2>/dev/null && ok "LIVE INJECTED-PASS (labelled, not live)" || no "LIVE not passed"
P=fx$R
# (the unit files are removed by cleanup; the driver's own setup assertion is the record)
grep -q "grep -q ^OnFailure=agent-loop-liveness-failed-$P.service\$ $INJECT_SD/agent-loop-liveness-$P.service" "$EV/driver/driver.log" && ! grep -q "^SETUP" "$EV/driver/results.tsv" && ok "liveness unit registered with exact OnFailure (setup assertion passed)" || no "OnFailure/unit registration"
grep -q "rm -f $INJECT_SD/agent-loop-fx$R.service" "$EV/driver/driver.log" && [ ! -e "$INJECT_SD/agent-loop-fx$R.service" ] && ok "unit files removed by exact name at cleanup" || no "unit files not removed"
grep -q "systemctl --user start agent-loop-$P.service agent-loop-liveness-$P.timer" "$INJ/argv.log" && ok "run + check units started by name from the unit dir" || no "units not started by name"
for id in $W $V $D $U; do grep -q " $id " "$HOME/.local/share/agent-deck/wake-send.log" 2>/dev/null || grep -q "$id" "$HOME/.local/share/agent-deck/wake-send.log" 2>/dev/null && ok "real wake delivered to $id (socket transport)" || no "no real wake to $id"; done
grep -q "anti-stub=\[" "$INJ/seat-runtime.log" && no "a task referenced a stream/helper" || ok "tasks carry no stream write or helper (anti-stub)"
[ "$(grep -c 'CLAIM .* rc=0 .* claim --config' "$INJ/seat-runtime.log")" -ge 2 ] && ok "worker and verifier used the candidate claim CLI" || no "claim CLI not used"
grep -q "DECISION OVERDUE" "$INJ/chat-notices.log" 2>/dev/null && ok "real notify-claude sent the labelled chat notice (curl injected)" || no "no chat notice"
grep -q "agent-deck launch" "$INJ/argv.log" && no "live driver launched seats" || ok "no seat launch in the live driver (consumes prepared IDs)"
python3 -c "import json; r=json.load(open('$INJ/registry.json')); assert not r" && ok "all four fixtures removed at cleanup" || no "fixtures remain"
[ -z "$(ls "$INJ/root/fx$R.db.caps" 2>/dev/null)" ] && ok "capability dir removed" || no "caps remain"
grep -rqE '[0-9a-f]{64}' "$EV/driver/archive/caps-redacted.txt" 2>/dev/null && no "hash-like bytes in caps record" || ok "caps record holds modes/paths only"
# attribution isolation (identity search in NEW shared writes) + planted negative
attr() { python3 - "$1" "$2" "$W0" "$E0" "$R|$INJ" <<'PY'
import re, sys
w, e, w0, e0, mark = sys.argv[1:6]; rx = re.compile(mark); hits = []
for p, n0 in ((w, int(w0)), (e, int(e0))):
    hits += [p for l in open(p, errors="replace").read().splitlines()[n0:] if rx.search(l)]
print("\n".join(hits)); sys.exit(1 if hits else 0)
PY
}
attr "$SHW" "$SHE" > "$EV/attribution.txt"; [ $? -eq 0 ] && ok "no shared write carries this run's identity" || no "shared write attributed"
cp "$SHE" "$INJ/esc-copy"; echo "{\"t\": 1, \"text\": \"$R planted\"}" >> "$INJ/esc-copy"
attr "$SHW" "$INJ/esc-copy" >/dev/null; [ $? -eq 1 ] && ok "attribution NEG detects a planted identity write" || no "attribution NEG missed"
kill $SEATPID 2>/dev/null
# ---- anti-stub negatives for LIVE mode (each must refuse before any effect)
neg() { env -u INJECT -u INJECT_SD "$@" > "$EV/neg.out" 2>&1; echo $?; }
[ "$(neg bash "$PKG/plans/live-p13-driver.sh" "$EV/inputs.env" run)" = 2 ] && grep -q "not an installed tool" "$EV/neg.out" && ok "NEG live refuses stub tools on PATH" || no "NEG stub tools accepted in live"
sed "s#^WAKE=.*#WAKE=$PKG/plans/fixture-wake.sh#" "$EV/inputs.env" > "$INJ/in2"; INJECT=1 INJECT_SD=$INJ/sd2 bash "$PKG/plans/live-p13-driver.sh" "$INJ/in2" run > "$EV/neg.out" 2>&1; [ $? = 2 ] && ok "NEG fixture/stub wake refused" || no "NEG fixture wake accepted"
sed "s#^WAKE_SHA=.*#WAKE_SHA=0000#" "$EV/inputs.env" > "$INJ/in3"; INJECT=1 INJECT_SD=$INJ/sd2 bash "$PKG/plans/live-p13-driver.sh" "$INJ/in3" run > "$EV/neg.out" 2>&1; [ $? = 2 ] && ok "NEG unpinned wake refused" || no "NEG unpinned wake accepted"
env -u INJECT -u INJECT_SD PATH=/usr/bin:/bin:$REALHOME/.local/bin EV_DIR=/tmp/x bash "$PKG/plans/live-p13-driver.sh" "$EV/inputs.env" run > "$EV/neg.out" 2>&1; [ $? = 2 ] && grep -q "EV_DIR" "$EV/neg.out" && ok "NEG live refuses the offline evidence override" || no "NEG EV_DIR accepted in live"
INJ=$INJ INJECT_SD=$INJ/sd "$H/stubs/systemctl" --user start not-registered.service 2>/dev/null; [ $? = 5 ] && ok "NEG an unregistered unit cannot start by name" || no "NEG unregistered unit started"
for p in $(ps -eo pid,args | grep -F "$INJ" | grep -v -e "grep -F" | awk '{print $1}'); do kill "$p" 2>/dev/null; done   # exact test-root processes only
echo "inject-test: $pass passed, $fail failed (INJECTED: not live proof)" | tee -a "$EV/test.log"; [ $fail -eq 0 ]
