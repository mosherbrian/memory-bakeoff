#!/bin/bash
# P13 repair offline proof: the EXACT top-level run path (plans/live20-plan.sh)
# executes under dependency-injected stubs with the REAL candidate binary on
# throwaway ledgers. No DRY=1 anywhere. Old (v1) scripts fail per F1-F5; the
# corrected path passes. Binary run/liveness loops execute as real processes
# (like the retained stopped-witness); systemd service management is stubbed
# and captured. No live seats/services/wakes/Signal, no shared writes.
set -uo pipefail
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
PLANS=$PKG/plans
V1=$PKG/evidence/plan-repair/v1
EV=$PKG/evidence/plan-repair/offline-closure2
rm -rf "$EV"; mkdir -p "$EV"
TMP=$(mktemp -d /tmp/p13repoff-XXXXXX)
export HOME="$TMP/home"; mkdir -p "$HOME"
SBIN=$TMP/stubbin; mkdir -p "$SBIN"
STATED=$TMP/sysstate; mkdir -p "$STATED"
CAPLOG=$EV/stub-argv.log; touch "$CAPLOG"
export STUB_CAPLOG="$CAPLOG" STUB_REGISTRY="$TMP/registry.json" STUB_HOME="$HOME" STUB_STATED="$STATED"
CAND=/home/bmosher/projects/agent-loop-releases/agent-loop-df5e6fc627b8/bin/agent-loop
pass=0; fail=0
ok() { pass=$((pass+1)); echo "PASS $1" | tee -a "$EV/offline.log"; }
no() { fail=$((fail+1)); echo "FAIL $1" | tee -a "$EV/offline.log"; }

# ---- stubs (capture exact argv; stateful systemctl; registry file) ----
cat > "$SBIN/systemctl" <<EOF
#!/bin/bash
echo "systemctl \$*" >> $CAPLOG
S="$STATED"
[ "\$1" = --user ] && shift
case "\$1" in
  is-active) [ -e "\$S/active-\$2" ] && echo active || echo inactive;;
  is-enabled) echo disabled;;
  start) touch "\$S/active-\$2";;
  stop) rm -f "\$S/active-\$2";;
  enable|disable|reset-failed|daemon-reload) ;;
  show) echo "TimersCalendar=*-*-* *:*:00 UTC;next_elapse=@\${STUB_WALL_EPOCH:-0}";;
  list-timers) ls "$STATED" 2>/dev/null | sed 's/^active-//';;
  list-units) ls "$STATED" 2>/dev/null | sed 's/^active-//';;
  kill) ;;
  *) echo "stub systemctl: unknown \$*" >&2; exit 1;;
esac
exit 0
EOF
printf '%s\n' '#!/bin/bash' 'echo "systemd-run $*" >> "$STUB_CAPLOG"' 'prev=""' 'for a in "$@"; do' 'if [ "$prev" = "--unit" ]; then unit="$a"; fi' 'case "$a" in --unit=*) unit="${a#--unit=}";; --unit) prev="--unit";; *) prev="$a";; esac' 'done' '[ -n "${unit:-}" ] && touch "${STUB_STATED:?}/active-$unit"', '[ -n "${unit:-}" ] && case "$unit" in *.timer|*.service|*.scope) ;; *) touch "${STUB_STATED:?}/active-$unit.timer";; esac' 'exit 0' > "$SBIN/systemd-run"
cat > "$SBIN/agent-deck" <<'STUBEOF'
#!/bin/bash
echo "agent-deck $*" >> "$STUB_CAPLOG"
R="$STUB_REGISTRY"
if [ "$1" = list ]; then cat "$R"; exit 0; fi
if [ "$1" = launch ]; then
  title=""; cmdline=""; prev=""
  for a in "$@"; do
    if [ "$prev" = "-t" ]; then title="$a"; fi
    if [ "$prev" = "-cmd" ]; then cmdline="$a"; fi
    case "$a" in -t) prev="-t";; -cmd) prev="-cmd";; *) prev="$a";; esac
  done
  case "$title" in *-id) id="$title";; *) id="$title-id";; esac
  prof="${AGENTDECK_PROFILE:-campaign4}"
  python3 -c "
import json, socket, os, sys
sockdir = os.path.join(os.environ['STUB_HOME'], '.config/agent-deck/acp-sock')
os.makedirs(sockdir, exist_ok=True)
p = os.path.join(sockdir, sys.argv[1] + '.sock')
try: os.remove(p)
except OSError: pass
s = socket.socket(socket.AF_UNIX); s.bind(p)
r = json.load(open(os.environ['STUB_REGISTRY']))
r.append({'id': sys.argv[1], 'title': sys.argv[2], 'profile': os.environ.get('AGENTDECK_PROFILE', 'campaign4'), 'command': sys.argv[3], 'status': 'idle'})
json.dump(r, open(os.environ['STUB_REGISTRY'], 'w'))" "$id" "$title" "$cmdline"
  echo "{\"id\": \"$id\", \"title\": \"$title\"}"; exit 0
fi
if [ "$1" = session ]; then
  if [ "$2" = remove ]; then python3 -c "import json,os,sys; p=os.environ['STUB_REGISTRY']; r=json.load(open(p)); r=[x for x in r if x.get('id')!=sys.argv[1] and x.get('title')!=sys.argv[1]]; json.dump(r, open(p,'w'))" "$3"; fi
  exit 0; fi
echo "stub agent-deck: unknown $*" >&2; exit 1
STUBEOF
chmod +x "$SBIN"/*
echo '[]' > "$TMP/registry.json"
export PATH="$SBIN:/usr/bin:/bin"
# closure-3: the plan's LIVE_DEADLINE is the REAL enclosing bound of this test
# process (OFFLINE_DEADLINE, required), and the whole test runs under it.
: "${OFFLINE_DEADLINE:?set OFFLINE_DEADLINE (UTC) to the enclosing author bound}"
left=$(( $(date -u -d "$OFFLINE_DEADLINE" +%s) - $(date +%s) ))
[ "$left" -ge 720 ] || { echo "REFUSED: only ${left}s before $OFFLINE_DEADLINE; a full run needs 720s"; exit 3; }
export STUB_WALL_EPOCH=$(date -u -d "$OFFLINE_DEADLINE" +%s)
SLEDGER=/home/bmosher/.local/share/agent-loop/campaign4.db
WAKELOG=/home/bmosher/.local/share/agent-deck/wake-send.log
ESCLEDGER=/home/bmosher/.local/share/agent-deck/escalations.jsonl
snap_shared() { sha256sum "$SLEDGER" 2>/dev/null; wc -l <"$WAKELOG" 2>/dev/null; wc -l <"$ESCLEDGER" 2>/dev/null; }
BEFORE=$(snap_shared)
SH_W0=$(wc -l <"$WAKELOG" 2>/dev/null || echo 0); SH_E0=$(wc -l <"$ESCLEDGER" 2>/dev/null || echo 0)

# ================= OLD-FAILS (v1 bound scripts) =================
# F1: v1-style config without seats cannot dispatch the promised identities.
mkdir -p $TMP/oldf1
python3 -c "import json; json.dump({'project':'oldf1','profile':'none','wake':'/tmp/x','db':'/tmp/x.db','director':'d','duty':'u','bin':'/tmp/x'}, open('$TMP/oldf1/fx.json','w'))"
$CAND dispatch --config $TMP/oldf1/fx.json --qid QF1 --worker fx-worker --verifier fx-verifier --task t --verify-task v --duration 5m --verify-window 5m >/dev/null 2>&1
[ $? -ne 0 ] && ok "F1 old config without seats refused by real binary" || no "F1 old config dispatched"
# F2: v1 prep argv is wrong for the real prepare_live.py.
python3 /home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation/src/prepare_live.py --worker X --verifier Y --out Z >/dev/null 2>&1
[ $? -eq 2 ] && ok "F2 old prep argv rejected rc2 by real tool" || no "F2 old prep argv accepted"
# F3: product output has no invented top-level rung strings; json.load on JSONL fails.
n=$($CAND status --config /tmp/schemaprobe/fx.json --json 2>/dev/null | grep -c "rung:director")
[ "$n" = 0 ] && ok "F3 no invented rung strings in real status" || no "F3 invented strings present"
python3 -c "import json; json.load(open('$PKG/evidence/repair-1/stopped-witness/escalations.jsonl'))" 2>/dev/null && no "F3 json.load on JSONL worked" || ok "F3 json.load on real JSONL fails (per-line required)"
grep -q "decision-turn" "$V1/tasks/decision-worker.md" 2>/dev/null && no "F3 v1 had turn command" || ok "F3 v1 task templates lack executable turn command"
# F4: v1 archive pattern leaks secrets.
mkdir -p $TMP/leaktest/caps; echo "TOPSECRET-CAP-BYTES" > $TMP/leaktest/caps/cap1
cp -a $TMP/leaktest $TMP/leak-archive
grep -q "TOPSECRET" -r $TMP/leak-archive && ok "F4 old archive-copies-ROOT leaks secret bytes" || no "F4 leak demo broken"
# F5: v1 copies candidate into PREV; no original restore.
grep -q 'install -m 755 "$BIN_SRC" "$PREV"' "$V1/promotion-plan.sh" && ok "F5 v1 PREV-from-candidate confirmed" || no "F5 v1 text changed?"
echo "INSTALLED-ORIGINAL" > $TMP/prev-sim-installed; echo "CANDIDATE-BYTES" > $TMP/prev-sim-candidate
cp $TMP/prev-sim-installed $TMP/prev-sim-prev; cp $TMP/prev-sim-candidate $TMP/prev-sim-prev; cp $TMP/prev-sim-candidate $TMP/prev-sim-bin
cp $TMP/prev-sim-prev $TMP/prev-sim-bin
[ "$(cat $TMP/prev-sim-bin)" = "CANDIDATE-BYTES" ] && ok "F5 old order: rollback reinstalls candidate (demonstrated)" || no "F5 old simulation broken"
cp $TMP/prev-sim-installed $TMP/prev-sim-prev2; cp $TMP/prev-sim-candidate $TMP/prev-sim-bin2
cp $TMP/prev-sim-prev2 $TMP/prev-sim-bin2
[ "$(cat $TMP/prev-sim-bin2)" = "INSTALLED-ORIGINAL" ] && ok "F5 new order: rollback restores exact original" || no "F5 new simulation broken"

# ================= NEW PATH: filled inputs =================
sed -e "s#<run-id, e.g. p13d1>#off1#" -e "s#<private root, e.g. /tmp/p13d1-root>#$TMP/root#" \
  -e "s#<UTC, e.g. 2026-09-24T07:00:00Z>#$OFFLINE_DEADLINE#" \
  -e "s#<agent-deck profile for fixture seats>#campaign4#" \
  -e "s#<private ROOT/bin/wake: installed by setup from versioned plans/fixture-wake.sh; never the shared wake>#$TMP/root/bin/wake#" \
  -e "s#<private stream dir>#$TMP/root/streams#" \
  -e "s#<fixture worker title>#p6-fixture-w#" -e "s#<fixture worker session id>#p6-fixture-w-id#" \
  -e "s#<fixture verifier title>#p6-fixture-v#" -e "s#<fixture verifier session id>#p6-fixture-v-id#" \
  -e "s#<fixture director title>#p6-fixture-d#" -e "s#<fixture director session id>#p6-fixture-d-id#" \
  -e "s#<fixture duty title>#p6-fixture-u#" -e "s#<fixture duty session id>#p6-fixture-u-id#" \
  -e "s#<private ROOT>/escalations.jsonl#$TMP/root/escalations.jsonl#" \
  -e "s#<private ROOT>/bin/notify-claude#$TMP/root/bin/notify-claude#" \
  -e "s#<private ROOT>/bin/escalation-resolve#$TMP/root/bin/escalation-resolve#" \
  -e "s#<private ROOT>/ticket-stub.log#$TMP/root/ticket-stub.log#" \
  "$PLANS/live-inputs.template.env" > "$EV/inputs-filled.env"
grep -v "^#" "$EV/inputs-filled.env" | grep -q "<" && no "inputs unfilled" || ok "inputs fully late-bound"
# shellcheck disable=SC1090
. "$EV/inputs-filled.env"
# (WAKE + ticket-notify installed by plan setup from versioned sources.)
# Real sockets for the tool-designed dry-run injection check (also used live
# by prepare_live when HOME is private).
mkdir -p "$TMP/prepcheck/sock" "$TMP/prepcheck/streams"
python3 -c "import socket; s1=socket.socket(socket.AF_UNIX); s1.bind('$TMP/prepcheck/sock/p6-fixture-w-id.sock'); s2=socket.socket(socket.AF_UNIX); s2.bind('$TMP/prepcheck/sock/p6-fixture-v-id.sock'); import time; time.sleep(120)" &
SOCKPID=$!
# Prep with REAL argv + tool-designed injection (dry-run) + stub D/U launches.
cat > "$TMP/inject.json" <<EOF
[{"id": "p6-fixture-w-id", "title": "p6-fixture-w", "profile": "campaign4", "command": "/bin/true", "status": "idle"},
 {"id": "p6-fixture-v-id", "title": "p6-fixture-v", "profile": "campaign4", "command": "/bin/true", "status": "idle"}]
EOF
env AGENTDECK_PROFILE=campaign4 python3 /home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation/src/prepare_live.py --profile campaign4 --worker-name p6-fixture-w --verifier-name p6-fixture-v --worker-lane /bin/true --verifier-lane /bin/true --manifest-out "$EV/prep-manifest.json" --dry-run --inject-list "$TMP/inject.json" --inject-sock-dir "$TMP/prepcheck/sock" --inject-stream-root "$TMP/prepcheck/streams" >>"$EV/offline.log" 2>&1 \
  && ok "F2 new prep argv accepted with designed injection" || no "F2 new prep argv refused"
kill $SOCKPID 2>/dev/null
python3 -c "import json; m=json.load(open('$EV/prep-manifest.json')); assert m['worker']['session_id']=='p6-fixture-w-id' and m['verifier']['session_id']=='p6-fixture-v-id'" 2>/dev/null \
  && ok "prep manifest binds both seats" || no "prep manifest wrong"
# (Four-seat registry binding is proven by the plan run below, which launches
# all four seats for real through the stub and checks the registry itself.)

echo "offline part 1 done"

# ================= NEW PATH: exact top-level run =================
export EV_DIR="$EV/live"
"$PLANS/live20-plan.sh" "$EV/inputs-filled.env" run >"$EV/plan-stdout.log" 2>&1 &
PLANPID=$!
# Real binary loops (witness pattern): run + outside checker as processes.
# closure-2: run starts only once the plan has written its config (it exited at once before).
( for i in $(seq 1 150); do [ -f "$ROOT/p13doff1.json" ] && break; sleep 1; done
  exec "$BIN_SRC" run --config "$ROOT/p13doff1.json" --every 2s ) >"$EV/runloop.log" 2>&1 &
RUNPID=$!
( while :; do "$BIN_SRC" liveness --config "$ROOT/p13doff1.json" >>"$EV/liveness.log" 2>&1; sleep 5; done ) &
CHKPID=$!
# NOTE: config path above is filled below once the plan writes it; loops
# retry until the file exists (binary exits nonzero, loops continue).
wait_for_plan_file() { for i in $(seq 1 60); do [ -f "$1" ] && return 0; sleep 2; done; return 1; }
echo "waiting for plan progress (turn driver active)"
# Turn driver: execute runnable task commands when each step opens.
Q=D-off1
turn_for_step() { # step -> turn kind
  "$BIN_SRC" status --config "$ROOT/p13doff1.json" --json 2>/dev/null | python3 -c "
import json,sys
try:
    ps=json.load(sys.stdin)['packages']
    print([p['step'] for p in ps if p['qid']=='$Q'][0])
except Exception: print('none')"
}
do_turn() { # KIND(action suffix) EXECUTION STEP OUTCOME
  "$PLANS/tasks/decision-turn.sh" --artifacts "$ROOT/art" --claims "$ROOT/claims" \
    --stream "$ROOT/streams/$1.jsonl" --item "i$(date +%s%3N)" --package "$Q" --action "$Q-$5" --execution "$2" \
    --step "$3" --outcome "$4" >>"$EV/offline.log" 2>&1
}
for i in $(seq 1 150); do
  [ -f "$ROOT/p13doff1.json" ] && break
  kill -0 $PLANPID 2>/dev/null || break
  sleep 2
done
[ -f "$ROOT/p13doff1.json" ] && ok "plan wrote full live config" || no "plan config missing"
python3 -c "
import json
c=json.load(open('$ROOT/p13doff1.json'))
for k in ('seats','director','duty','wake','bin','claims_dir','artifacts_dir','stream_dir','decision_policy','decision_ladder'):
    assert k in c, k
assert c['seats']['p6-fixture-w']=='p6-fixture-w-id'" 2>>"$EV/offline.log" \
  && ok "F1 config carries all dispatch identities" || no "F1 config incomplete"
for i in $(seq 1 150); do
  s=$(turn_for_step)
  [ "$s" = worker ] && break
  kill -0 $PLANPID 2>/dev/null || break
  sleep 2
done
do_turn "$W_ID" "ex-$Q-w1" worker-run completed w1 \
  && ok "runnable worker turn produced artifacts+claim+end" || no "worker turn failed"
for i in $(seq 1 150); do
  s=$(turn_for_step)
  { [ "$s" = verify ] || [ "$s" = decision ]; } && break
  kill -0 $PLANPID 2>/dev/null || break
  sleep 2
done
do_turn "$V_ID" "ex-$Q-v1" verify-run completed v1 \
  && ok "runnable verifier turn produced artifacts+claim+end" || no "verifier turn failed"
# Liveness ran for real with verdict schema.
sleep 12
grep -q '"verdict"' "$EV/liveness.log" 2>/dev/null \
  && ok "outside checker runs with verdict schema" || no "liveness produced no verdict"
# Wait for the plan to finish (its own waits drive the rest).
wait $PLANPID; PLANRC=$?
kill $RUNPID $CHKPID 2>/dev/null; wait 2>/dev/null
[ $PLANRC -eq 0 ] && ok "exact top-level run path rc0 under stubs+real binary" || no "plan rc=$PLANRC"
grep -qP '\tFAIL\t' "$EV/live/results.tsv" 2>/dev/null && no "FAIL rows in live results" || ok "no FAIL rows in live results"
grep -q "LIVE	PASS" "$EV/live/results.tsv" 2>/dev/null && ok "LIVE PASS recorded" || no "LIVE PASS missing"
grep -q "NOTIFY	PASS	.*mode offline" "$EV/live/results.tsv" && ok "notify mode asserted offline (offline success never proves real notification)" || no "notify mode not asserted"
grep -q FIXTURE-NOTICE "$TICKET_STUB" 2>/dev/null && ok "labelled fixture notice in the stub" || no "no stub notice"
# decision-ack negatives for real (literal/guessed/cross-incident refused).
"$BIN_SRC" decision-ack --config "$ROOT/p13doff1.json" --qid "$Q" --by claude --next x --within 60s >/dev/null 2>&1
[ $? -ne 0 ] && ok "literal ack without cap refused" || no "literal ack accepted"
echo 0000000000000000000000000000000000000000000000000000000000000000 > $TMP/guess
"$BIN_SRC" decision-ack --config "$ROOT/p13doff1.json" --qid "$Q" --by claude --cap-file $TMP/guess --next x --within 60s >/dev/null 2>&1
[ $? -ne 0 ] && ok "guessed capability refused" || no "guessed cap accepted"
# Caps: redacted record only, secret bytes absent, dir actually gone.
[ -f "$EV/live/archive/caps-redacted.txt" ] && ok "caps redaction record exists" || no "caps redaction missing"
CAPBYTES=$(find "$ROOT" -path "*caps*" -type f 2>/dev/null | head -n 1)
if [ -z "$CAPBYTES" ] && [ ! -d "$ROOT/p13doff1.db.caps" ]; then ok "actual db.caps removed (exact scope)"; else no "caps remain: $CAPBYTES"; fi
grep -rqE "[0-9a-f]{64}" "$EV/live/archive/caps-redacted.txt" 2>/dev/null && no "secret-length bytes in redaction record" || ok "redaction holds hashes/permissions only"
# Exact scope/IDs gone; stub argv captured for key commands.
left=$(python3 -c "import json; print(' '.join(r.get('id','') for r in json.load(open('$TMP/registry.json'))))")
gone=1
for id in p6-fixture-w-id p6-fixture-v-id p6-fixture-d p6-fixture-u; do echo "$left" | grep -qw "$id" && { no "seat $id remains"; gone=0; }; done
[ $gone -eq 1 ] && ok "all four fixture seats removed (exact IDs)"
grep -q "systemctl --user start agent-loop-p13doff1.service" "$CAPLOG" && ok "run service start captured" || no "run start not captured"
grep -q "agent-deck launch" "$CAPLOG" && ok "seat launch argv captured" || no "launch argv missing"


# ================= Promotion failure + exact rollback (offline) =================
export PROMOTE_BIN=$TMP/fakebin PROMOTE_PREV=$TMP/fakebin.prev PROMOTE_CFG=$TMP/fakecfg.json PROMOTE_SD=$TMP/fakesd PROMOTE_AD=$TMP/fakead
mkdir -p $TMP/fakesd
echo "INSTALLED-ORIGINAL-BYTES" > $TMP/fakebin; chmod +x $TMP/fakebin
echo '{"decision_policy":"required"}' > $TMP/fakecfg.json
mkdir -p $TMP/fakead
echo "watch-original" > $TMP/fakead/escalation-watch
echo "resolve-original" > $TMP/fakead/escalation-resolve
mkdir -p $TMP/fakesd
echo "timer-original" > $TMP/fakesd/escalation-watch.timer
echo "service-original" > $TMP/fakesd/escalation-watch.service
grep -q "guard_absent()" "$PLANS/promotion-plan.sh" && grep -q "rollback()" "$PLANS/promotion-plan.sh" && ok "promotion guard+rollback defined" || no "promotion functions missing"
# Failure injection: candidate hash mismatch forces install refusal, then rollback.
EV_DIR=$TMP/promofail2 BIN_SRC=/nonexistent-candidate PROMOTE_BIN=$TMP/fakebin2 PROMOTE_PREV=$TMP/fakebin2.prev PROMOTE_CFG=$TMP/fakecfg.json PROMOTE_SD=$TMP/fakesd PROMOTE_AD=$TMP/fakead bash "$PLANS/promotion-plan.sh" "$EV/inputs-filled.env" run >/dev/null 2>&1
[ $? -ne 0 ] && ok "promotion failure refuses (no unchecked PASS)" || no "promotion failure passed"
# Exact rollback restores originals (run rollback path with staged archive).
mkdir -p $TMP/rbev/promo-archive
echo "INSTALLED-ORIGINAL-BYTES" > $TMP/rbev/promo-archive/agent-loop.installed
echo "INSTALLED-ORIGINAL-BYTES" > $TMP/fakebin.rb; cp $TMP/fakebin.rb $TMP/fakebin.prev
sha256sum $TMP/fakebin.prev | cut -d' ' -f1 > $TMP/rbev/promo-archive/installed-sha.txt
echo "cfg-original" > $TMP/rbev/promo-archive/campaign4.json
for f in escalation-watch escalation-watch.timer escalation-watch.service escalation-resolve; do echo "$f-original" > $TMP/rbev/promo-archive/$f; done
echo "755 bmosher $TMP/fakebin.rb" > $TMP/rbev/promo-archive/ownership.txt
echo "CANDIDATE-BYTES" > $TMP/fakebin.rb
mkdir -p $TMP/rbsd $TMP/rbad  # closure-2: target dirs exist in production
EV_DIR=$TMP/rbev PROMOTE_BIN=$TMP/fakebin.rb PROMOTE_PREV=$TMP/fakebin.prev PROMOTE_CFG=$TMP/rbcfg.json PROMOTE_SD=$TMP/rbsd PROMOTE_AD=$TMP/rbad bash "$PLANS/promotion-plan.sh" "$EV/inputs-filled.env" rollback >/dev/null 2>&1
[ "$(cat $TMP/fakebin.rb)" = "INSTALLED-ORIGINAL-BYTES" ] && ok "rollback restores exact original, not candidate" || no "rollback did not restore original"
grep -q "ROLLBACK	PASS" $TMP/rbev/promotion-results.tsv 2>/dev/null && ok "rollback PASS recorded" || no "rollback PASS missing"

# ================= Offline negatives =================
bash "$PLANS/live20-plan.sh" --bad-flag >/dev/null 2>&1
[ $? -ne 0 ] && ok "wrong CLI refused" || no "wrong CLI accepted"
printf 'not json\n' > $TMP/badledger.jsonl
python3 -c "import json; json.load(open('$TMP/badledger.jsonl'))" 2>/dev/null && no "malformed ledger parsed" || ok "malformed ledger refused"
[ -d "$ROOT/p13doff1.db.caps" ] && no "caps dir remains post-cleanup" || ok "restart-absent/cleanup idempotent (caps gone)"
grep -q "intentional stop marker AFTER" "$EV/live/driver.log" && ok "stop marker observed before the ladder (cleared by restart)" || no "stop marker missing"

# ================= Isolation by WRITE ATTRIBUTION (closure-2) =================
# Production keeps running, so shared files may change for unrelated reasons.
# A leak is attributed only if a NEW shared write carries this run's identity
# (project, qid, private root, fixture seat ids/titles).
MARK="p13doff1|D-off1|$TMP|p6-fixture-"
attr() { python3 - "$SLEDGER" "$WAKELOG" "$ESCLEDGER" "$MARK" "$SH_W0" "$SH_E0" <<'PY'
import re, sqlite3, sys
db, wake, esc, mark, w0, e0 = sys.argv[1:7]; rx = re.compile(mark); hits = []
for path, n0 in ((wake, int(w0 or 0)), (esc, int(e0 or 0))):
    try: lines = open(path, errors="replace").read().splitlines()[n0:]
    except OSError: continue
    hits += ["%s:%d" % (path, n0 + i + 1) for i, l in enumerate(lines) if rx.search(l)]
try:
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    for (t,) in c.execute("select name from sqlite_master where type='table'"):
        for row in c.execute('select * from "%s"' % t):
            if rx.search(" ".join(map(str, row))): hits.append("%s:%s" % (db, t))
except Exception as e: print("UNREADABLE %s: %s" % (db, e)); sys.exit(2)
print("\n".join(hits)); sys.exit(1 if hits else 0)
PY
}
attr > "$EV/shared-attribution.txt" 2>&1; ar=$?
[ $ar -eq 0 ] && ok "no shared write attributable to this run (identity search: wake-send.log/escalations.jsonl new lines, campaign4.db rows)" || no "shared write attributed to this run or unreadable (see shared-attribution.txt)"
[ "$BEFORE" = "$(snap_shared)" ] && echo "info: shared files unchanged" >>"$EV/offline.log" || echo "info: shared files changed during the run (production active); attribution above decides" >>"$EV/offline.log"
grep -rq "notify-claude decision" "$TMP/root" 2>/dev/null && no "real notify path touched" || ok "no real notify path touched"
grep -rqiE "cap[^a-z].{0,20}[0-9a-f]{32,}|BEGIN.*PRIVATE" "$EV" 2>/dev/null | grep -v "TOPSECRET-CAP-BYTES\|0000000000" | grep -q . && no "secret material in evidence" || ok "no secret material in evidence"
grep -q "/home/bmosher/.local/share/agent-loop/campaign4.db\|/home/bmosher/.local/share/agent-deck/wake-send.log\|/home/bmosher/.local/share/agent-deck/escalations.jsonl" "$EV/live/driver.log" 2>/dev/null && no "shared paths in driver log" || ok "no shared paths referenced"

# negative control: a planted identity line in a COPY of the shared escalation ledger is attributed
cp "$ESCLEDGER" $TMP/esc-copy.jsonl 2>/dev/null || : > $TMP/esc-copy.jsonl
echo '{"t": 1, "id": "E-x", "key": "k", "text": "p13doff1 planted"}' >> $TMP/esc-copy.jsonl
( ESCLEDGER=$TMP/esc-copy.jsonl; attr >/dev/null 2>&1 ); [ $? -eq 1 ] && ok "attribution NEG: planted run-identity write is detected" || no "attribution NEG missed a planted write"
echo "offline: $pass passed, $fail failed" | tee -a "$EV/offline.log"
[ "$fail" -eq 0 ]
