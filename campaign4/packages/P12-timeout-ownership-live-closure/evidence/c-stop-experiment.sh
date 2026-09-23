#!/bin/bash
# C: time a real `systemctl --user stop` of an idle `agent-loop run` in a transient Type=notify unit
# with the template's stop/watchdog settings. Unit name p12test-stop-<LABEL>-<pid>; removed at the end.
# Usage: c-stop-experiment.sh BINARY LABEL notifier|fallback [SIGTERM|SIGINT|marker|restart]
#   marker: `agent-loop stop` (intentional stop) instead of systemctl stop; expects exit 64, no restart.
#   restart: systemctl restart twice, then stop; each timed; the ledger's pass count and outbox are read.
set -u
B=$1; LABEL=$2; MODE=$3; SIG=${4:-SIGTERM}; X=$(mktemp -d /tmp/p12-stop-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
UNIT=p12test-stop-$LABEL-$$
printf '#!/bin/sh\necho "[]"\n' > $S/agent-deck; printf '#!/bin/sh\necho "wake: $1 -> started"\n' > $S/wake; chmod +x $S/*
SD=$X/stream; [ "$MODE" = fallback ] && SD=$X/no-such-dir
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$SD", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "d", "duty": "u", "unit": "$UNIT.service", "seats": {"d": "D1", "u": "U1"}, "bin": "$B", "agent_deck": "$S/agent-deck"}
EOF
echo "== $(sha256sum $B | cut -c1-16) mode=$MODE signal=$SIG unit=$UNIT"
systemd-run --user --quiet --unit=$UNIT -p Type=notify -p NotifyAccess=main -p TimeoutStopSec=20 -p WatchdogSec=90 -p KillSignal=$( [ "$SIG" = SIGINT ] && echo SIGINT || echo SIGTERM ) -p Restart=always -p RestartSec=5 -p RestartPreventExitStatus=64 -p SuccessExitStatus=64 -- $B run --config $X/fx.json
echo "start rc=$? active=$(systemctl --user is-active $UNIT)"
sleep 3
if [ "$SIG" = marker ]; then
  t0=$(date +%s.%N); $B stop --config $X/fx.json >/dev/null; rc=$?
  while [ "$(systemctl --user is-active $UNIT)" = active ]; do sleep 0.05; done; t1=$(date +%s.%N)
  echo "STOP_SECONDS=$(python3 -c "print(round($t1-$t0,3))") (agent-loop stop, rc=$rc)"; sleep 7
  echo "after 7 s (RestartSec would be 5 s): active=$(systemctl --user is-active $UNIT) NRestarts=$(systemctl --user show $UNIT -p NRestarts --value)"
elif [ "$SIG" = restart ]; then
  for i in 1 2; do t0=$(date +%s.%N); systemctl --user restart $UNIT; t1=$(date +%s.%N); echo "RESTART_$i seconds=$(python3 -c "print(round($t1-$t0,3))") active=$(systemctl --user is-active $UNIT)"; sleep 3; done
  t0=$(date +%s.%N); systemctl --user stop $UNIT; rc=$?; t1=$(date +%s.%N)
  echo "STOP_SECONDS=$(python3 -c "print(round($t1-$t0,3))") stop_rc=$rc"
  $B status --config $X/fx.json --json | head -c 200; echo
else
  t0=$(date +%s.%N); systemctl --user stop $UNIT; rc=$?; t1=$(date +%s.%N)
  echo "STOP_SECONDS=$(python3 -c "print(round($t1-$t0,3))") stop_rc=$rc"
fi
systemctl --user show $UNIT -p Result -p ExecMainCode -p ExecMainStatus 2>/dev/null | tr '\n' ' '; echo
echo "journal: $(journalctl --user -u $UNIT --since "-2min" -o cat --no-pager | grep -E 'timed out|SIGABRT|no inotify|Deactivated|Stopped|Main process exited|stop requested' | cut -c1-110 | tr '\n' '|')"
systemctl --user reset-failed $UNIT 2>/dev/null; echo "cleanup: $(systemctl --user is-active $UNIT 2>&1)"
