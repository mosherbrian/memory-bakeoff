#!/bin/bash
# E: do transient timers keep their schedule across real `systemctl --user daemon-reload`?
# Two timers with the same target instant: --on-active (monotonic) and --on-calendar with explicit UTC.
# Both run a one-line command that writes the firing time. Names p12test-{mono,cal}-<pid>; stopped at the end.
# daemon-reload re-reads EVERY user unit file (inventory below): it is a host effect, never zero.
set -u
X=$(mktemp -d /tmp/p12-reload-XXXX); T=${1:-60}; R=${2:-3}
now=$(date +%s); tgt=$((now + T)); cal="$(date -u -d @$tgt '+%Y-%m-%d %H:%M:%S') UTC"
echo "== reload inventory: $(systemctl --user list-unit-files --no-legend | wc -l) user unit files; $(systemctl --user list-units --all --no-legend | wc -l) loaded units"
echo "armed at $(date -u +%FT%T.%3NZ); target $(date -u -d @$tgt +%FT%TZ) (+${T}s); calendar spec: $cal"
systemd-run --user --quiet --unit=p12test-mono-$$ --timer-property=AccuracySec=1s --on-active=${T}s /bin/sh -c "date -u +%s.%N > $X/fired-mono"
systemd-run --user --quiet --unit=p12test-cal-$$ --timer-property=AccuracySec=1s --on-calendar="$cal" /bin/sh -c "date -u +%s.%N > $X/fired-cal"
snap() { for k in mono cal; do echo "   $1 $k: $(systemctl --user show p12test-$k-$$.timer -p NextElapseUSecRealtime -p NextElapseUSecMonotonic -p TimersMonotonic -p TimersCalendar -p ActiveState | tr '\n' ' ')"; done; }
snap "before (t=$(date -u +%T.%3N))"
for i in $(seq 1 $R); do sleep 5; systemctl --user daemon-reload; echo "reload $i at $(date -u +%T.%3N) rc=$?"; snap "after reload $i"; done
while [ $(date +%s) -lt $((tgt + 15)) ]; do sleep 2; done
for k in mono cal; do
  if [ -s $X/fired-$k ]; then echo "FIRED_$k=$(python3 -c "print(round($(cat $X/fired-$k) - $tgt, 3))") s after target"; else echo "FIRED_$k=NO (not by target+15s)"; fi
  systemctl --user stop p12test-$k-$$.timer 2>/dev/null; systemctl --user reset-failed p12test-$k-$$.service p12test-$k-$$.timer 2>/dev/null
done
echo "cleanup: $(systemctl --user list-units --all --no-legend "p12test-*-$$*" | wc -l) units left"
