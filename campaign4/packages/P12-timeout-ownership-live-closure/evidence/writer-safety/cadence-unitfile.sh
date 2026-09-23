#!/bin/bash
# Real unit-file timer (OnActiveSec=45s, OnUnitActiveSec=45s, AccuracySec=1s, as agent-loop-liveness@.timer)
# running the candidate `agent-loop liveness` against a stub config, across repeated REAL daemon-reloads.
# Unit files p12test-cadence-<pid>.{service,timer} in ~/.config/systemd/user; removed at the end.
# Usage: cadence-unitfile.sh BINARY SECONDS RELOAD_EVERY
set -u
B=$1; DUR=${2:-300}; RE=${3:-20}; X=$(mktemp -d /tmp/p12-cadence-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
N=p12test-cadence-$$; SD=$HOME/.config/systemd/user
printf '#!/bin/sh\necho "[]"\n' > $S/agent-deck; printf '#!/bin/sh\necho "wake: $1 -> started"\n' > $S/wake
printf '#!/bin/sh\ncase "$*" in *show*) printf "ActiveState=inactive\\nSubState=dead\\n";; esac\n' > $S/systemctl; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "d", "duty": "u", "unit": "fx.service", "seats": {"d": "D1", "u": "U1"}, "bin": "$B", "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl"}
EOF
$B run --config $X/fx.json --once >/dev/null 2>&1
cat > $SD/$N.service <<EOF
[Unit]
Description=P12 cadence test (isolated, no seats)
[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo "start \$(date -u +%%s.%%N)" >> $X/checks.log; $B liveness --config $X/fx.json >/dev/null 2>&1; echo "done \$(date -u +%%s.%%N)" >> $X/checks.log'
EOF
cat > $SD/$N.timer <<EOF
[Unit]
Description=P12 cadence test timer
[Timer]
OnActiveSec=45s
OnUnitActiveSec=45s
AccuracySec=1s
RandomizedDelaySec=0
EOF
systemctl --user daemon-reload; t0=$(date +%s.%N); systemctl --user start $N.timer; echo "timer started at $t0 ($(date -u +%T))"
: > $X/reloads.log; end=$(( ${t0%.*} + DUR ))
if [ "$RE" = 0 ]; then sleep $DUR; else   # RELOAD_EVERY 0: control run, no reloads
while [ $(date +%s) -lt $end ]; do sleep $RE; systemctl --user daemon-reload; echo "$(date -u +%s.%N)" >> $X/reloads.log; done; fi
systemctl --user stop $N.timer $N.service; rm -f $SD/$N.service $SD/$N.timer; systemctl --user daemon-reload; systemctl --user reset-failed $N.timer $N.service 2>/dev/null
echo "reloads: $(wc -l < $X/reloads.log) (every ${RE}s)"
[ -e $X/checks.log ] || echo "NO CHECK RAN in ${DUR}s (checks.log absent)"
[ -e $X/checks.log ] && python3 - $X/checks.log $t0 <<'PY'
import sys
t0 = float(sys.argv[2]); st = [float(l.split()[1]) for l in open(sys.argv[1]) if l.startswith("start")]
dn = [float(l.split()[1]) for l in open(sys.argv[1]) if l.startswith("done")]
print("checks started (s after timer start):", [round(x - t0, 2) for x in st])
gaps = [round(b - a, 2) for a, b in zip(st, st[1:])]
print("gaps between starts:", gaps)
print("check durations:", [round(d - s, 3) for s, d in zip(st, dn)])
print("MAX_GAP=%s FIRST=%s EXPECTED=45 (OnUnitActiveSec counts from the previous start)" % (max(gaps) if gaps else None, round(st[0] - t0, 2) if st else None))
PY
echo "cleanup: $(systemctl --user list-units --all --no-legend "$N*" | wc -l) units left, files $(ls $SD/$N.* 2>/dev/null | wc -l)"
