#!/bin/bash
# P10 liveness cases through the real CLI, with stub systemctl/wake/agent-deck.
# Usage: liveness-cases.sh BINARY   (prints each case and its outcome)
# Cases: damaged incident state (malformed, truncated, partial, unreadable),
# future pass time (rollback, boundary), prior-incarnation pass (fresh, PID reuse,
# missing identity, restart before the first pass). No real service or seat.
set -u
A=$1; X=$(mktemp -d /tmp/p10-cases-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
printf '#!/bin/sh\necho "$1 $(echo "$2" | head -c 60)" >> %s/wake.log; echo "wake: $1 -> started"\n' $X > $S/wake
printf '#!/bin/sh\ncat %s/unit.props\n' $X > $S/systemctl
chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "agent-loop@fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl"}
EOF
C="--config $X/fx.json"
INV=0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
now=$(date +%s)
unit() { # ActiveState InvocationID MainPID started-seconds-ago
  printf 'ActiveState=%s\nSubState=running\nResult=success\nNRestarts=0\nInvocationID=%s\nMainPID=%s\nExecMainStartTimestamp=@%s\n' "$1" "$2" "$3" $(( $(date +%s) - $4 )) > $X/unit.props; }
pass() { # seconds-offset invocation pid
  python3 - "$X/fx.db" "$1" "$2" "$3" <<'PY'
import sqlite3, sys, json, datetime
db, off, inv, pid = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=off)).strftime("%Y-%m-%dT%H:%M:%SZ")
p = {"at": at, "pid": pid, "pass": 9, "advanced": 0, "open_packages": 0, "error_streak": 0}
if inv: p["invocation"] = inv
c = sqlite3.connect(db); c.execute("INSERT OR REPLACE INTO driver_kv (key, value) VALUES ('loop-pass', ?)", (json.dumps(p),)); c.commit()
PY
}
check() { out=$($A liveness $C 2>&1); rc=$?; w=0; [ -f $X/wake.log ] && w=$(wc -l < $X/wake.log); echo "   rc=$rc wakes=$w $(echo "$out" | tail -1 | cut -c1-230)"; }
reset() { rm -f $X/fx.db.liveness.json* $X/wake.log; }
unit active $INV 4242 3600
$A run $C --once >/dev/null 2>&1
echo "== baseline: fresh pass from the current incarnation"; reset; pass 0 $INV 4242; check
echo "== 1a damaged incident state: malformed JSON"; reset; pass 0 $INV 4242; printf '{not json' > $X/fx.db.liveness.json; check; check; ls $X | grep liveness | tr '\n' ' '; echo
echo "== 1b truncated state holding an open incident with an ack"; reset; printf '{"open": {"id": "L20260923T100000Z", "state": "hung", "opened_at": "2026-09-23T10:00:00Z", "duty_wake": {"at": "2026-09-23T10:00:00Z", "to": "fx-duty", "status": "sent"}, "ack": {"by": "fx-duty", "next_action": "restart", "response_deadline": "2026-09-23T10:15' > $X/fx.db.liveness.json; check; ls $X | grep liveness | tr '\n' ' '; echo
echo "== 1c partially populated: open incident without an id"; reset; printf '{"open": {"state": "hung"}}' > $X/fx.db.liveness.json; check
echo "== 1d unreadable state file"; reset; printf '{}' > $X/fx.db.liveness.json; chmod 000 $X/fx.db.liveness.json; check; check; chmod 644 $X/fx.db.liveness.json; ls $X | grep liveness | tr '\n' ' '; echo
echo "== 2a pass time 6 s in the future"; reset; pass 6 $INV 4242; check
echo "== 2b pass time exactly 5 s in the future (tolerance boundary)"; reset; pass 5 $INV 4242; check
echo "== 2c clock stepped back 10 min after the pass"; reset; pass 600 $INV 4242; check
echo "== 3a fresh pass from a previous incarnation, unit started 10 min ago"; reset; pass 0 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 4242; check
echo "== 3b same, restart 20 s ago, before its first pass (startup grace)"; reset; unit active $INV 5151 20; pass 0 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 4242; check
echo "== 3c PID reuse: same PID, previous invocation"; reset; unit active $INV 4242 3600; pass 0 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 4242; check
echo "== 3d pass without any incarnation identity"; reset; pass 0 "" 4242; check
echo "== 3e unit identity unreadable (no InvocationID)"; reset; pass 0 $INV 4242; printf 'ActiveState=active\nSubState=running\nResult=success\nNRestarts=0\n' > $X/unit.props; check
echo "== 3f pass from this invocation but another PID"; reset; unit active $INV 4242 3600; pass 0 $INV 999; check
echo "(workdir $X)"
