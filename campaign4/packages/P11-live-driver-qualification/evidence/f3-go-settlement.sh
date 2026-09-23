#!/bin/bash
# F3 offline: how L2 settles, through the FROZEN agent-loop CLI with injected transport
# (stub wake, agent-deck, systemctl, systemd-run). No real unit, timer or seat.
# Usage: f3-go-settlement.sh BINARY
set -u
A=$1; X=$(mktemp -d /tmp/p11-f3-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
printf '#!/bin/sh\necho "$1 $(echo "$2" | tr "\\n" " " | head -c 90)" >> %s/wake.log; echo "wake: $1 -> started"\n' $X > $S/wake
printf '#!/bin/sh\ncase "$*" in *show*) cat %s/unit.props;; *) echo "systemctl $*" >> %s/systemctl.log;; esac\n' $X $X > $S/systemctl
printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run
chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "agent-loop@fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"; INV=0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
printf 'ActiveState=active\nSubState=running\nResult=success\nNRestarts=0\nInvocationID=%s\nMainPID=%s\nExecMainStartTimestamp=@%s\n' $INV $$ $(( $(date +%s) - 3600 )) > $X/unit.props
export INVOCATION_ID=$INV
step() { $A expose $C --json 2>/dev/null | python3 -c "import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0])"; }
wk() { [ -f $X/wake.log ] || { echo 0; return; }; grep -c "^$1 " $X/wake.log; }
unitpid() { # stub systemd reports the last run process as the unit's main PID
  local pid; pid=$(python3 -c "import sqlite3,json;print(json.loads(sqlite3.connect('$X/fx.db').execute(\"select value from driver_kv where key='loop-pass'\").fetchone()[0])['pid'])")
  sed -i "s/^MainPID=.*/MainPID=$pid/" $X/unit.props; }
live() { unitpid; $A liveness $C 2>/dev/null | tail -1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['verdict']['state'])"; }
ok=0; bad=0
assert() { if [ "$2" = "$3" ]; then echo "PASS  $1: $2"; ok=$((ok+1)); else echo "FAIL  $1: got '$2' want '$3'"; bad=$((bad+1)); fi; }
echo "== binary $(sha256sum $A | cut -c1-16)  workdir $X"
$A run $C --once >/dev/null 2>&1
assert "idle loop is rest" "$(live)" rest
$A dispatch $C --qid L2 --worker fx-worker --verifier fx-verifier --task "write nothing, claim nothing" --verify-task "verify" --duration 20s --verify-window 5m >/dev/null 2>&1
$A run $C --once >/dev/null 2>&1
assert "L2 in worker step after dispatch" "$(step L2)" worker
assert "worker woken once" "$(wk W1)" 1
assert "NEGATIVE: open L2 is not rest" "$(live)" ok
cb=$(tail -1 $X/systemd-run.log); echo "   armed: ${cb:0:160}"
# the restart after SIGKILL: a new run process; no resend (original L2 assertion)
$A run $C --once >/dev/null 2>&1
assert "restart: no second dispatch to the worker" "$(wk W1)" 1
# the deadline timer fires (the command systemd-run was given, run exactly, after the deadline)
sleep 22
cbargs=$(echo "$cb" | grep -o -- "timer-callback.*")
w0=$(wk W1); d0=$(wk D1)
$A $cbargs > $X/cb1.out 2>&1; echo "   callback: $(head -c 160 $X/cb1.out)"
assert "callback decision" "$(python3 -c "import json;print(json.load(open('$X/cb1.out'))['decision'])" 2>&1)" interrupted
assert "L2 settled step" "$(step L2)" timed-out
assert "one /cancel to the worker" "$(( $(wk W1) - w0 ))" 1
assert "one director wake" "$(( $(wk D1) - d0 ))" 1
$A run $C --once >/dev/null 2>&1
assert "rest once L2 is settled (no open work)" "$(live)" rest
# replay of the same callback: nothing new
w1=$(wk W1); d1=$(wk D1)
$A $cbargs > $X/cb2.out 2>&1; echo "   replay: $(head -c 160 $X/cb2.out)"
assert "replay decision" "$(python3 -c "import json;print(json.load(open('$X/cb2.out'))['decision'])" 2>&1)" already-handled
assert "replay: no worker/director effect" "$(( $(wk W1) - w1 )):$(( $(wk D1) - d1 ))" 0:0
# a director decision on the timed-out package: accepted or refused by the core?
$A decide $C --qid L2 --kind budget_spent --ref P11-f3 --reason "L2 fault case settled by its deadline" > $X/decide.out 2>&1; drc=$?
echo "   decide rc=$drc: $(head -c 200 $X/decide.out)   step now: $(step L2)"
# L6 afterwards: its counts see no L2 effect
$A dispatch $C --qid L6 --worker fx-worker --verifier fx-verifier --task "no claim" --verify-task "verify" --duration 20s --verify-window 5m >/dev/null 2>&1
c1=$(wk W1); dd1=$(wk D1)
$A run $C --once >/dev/null 2>&1; sleep 22
cb6=$(tail -1 $X/systemd-run.log | grep -o -- "timer-callback.*"); $A $cb6 > $X/cb6.out 2>&1
assert "L6: one /cancel only after its dispatch (no L2 effect)" "$(( $(wk W1) - c1 ))" 1
assert "L6: one director wake" "$(( $(wk D1) - dd1 ))" 1
assert "L6 step" "$(step L6)" timed-out
echo "== $ok PASS, $bad FAIL"; [ $bad -eq 0 ]
