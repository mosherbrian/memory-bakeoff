#!/bin/bash
# Real unit-file liveness timers from the EXACT templates (old: 844d156 release, new: candidate), installed as the
# live driver installs them (sed of %h paths and %i only), both running at once, with a REAL daemon-reload every
# RELOAD_EVERY s for DURATION s. Check starts/ends come from the journal. Private instance names, stub config,
# no seats; unit files removed at the end. Usage: cadence-templates.sh BINARY OLD_TEMPLATE_DIR NEW_TEMPLATE_DIR DURATION RELOAD_EVERY
set -u
B=$1; OLD=$2; NEW=$3; DUR=${4:-300}; RE=${5:-20}; X=$(mktemp -d /tmp/p12-tpl-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
SD=$HOME/.config/systemd/user
printf '#!/bin/sh\necho "[]"\n' > $S/agent-deck; printf '#!/bin/sh\necho "wake: $1 -> started"\n' > $S/wake
printf '#!/bin/sh\ncase "$*" in *show*) printf "ActiveState=inactive\\nSubState=dead\\n";; esac\n' > $S/systemctl; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "d", "duty": "u", "unit": "fx.service", "seats": {"d": "D1", "u": "U1"}, "bin": "$B", "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl"}
EOF
$B run --config $X/fx.json --once >/dev/null 2>&1
units=""
for kind in old new; do
  dir=$OLD; [ $kind = new ] && dir=$NEW
  I=p12tpl$kind$$; LU=agent-loop-liveness-$I
  sub="s#%h/.local/bin/agent-loop#$B#g; s#%h/.config/agent-loop/%i.json#$X/fx.json#g; s#%i#$I#g"
  sed "$sub" $dir/agent-loop-liveness@.service > $SD/$LU.service; sed "$sub" $dir/agent-loop-liveness@.timer > $SD/$LU.timer
  echo "== $kind template: $(sha256sum $dir/agent-loop-liveness@.timer | cut -c1-16) -> $LU.timer [Timer]: $(sed -n '/\[Timer\]/,/\[Install\]/p' $SD/$LU.timer | grep -v '^#' | grep -v '^\[' | tr '\n' ' ')"
  units="$units $LU"
done
systemctl --user daemon-reload; t0=$(date +%s); for u in $units; do systemctl --user start $u.timer; done
echo "timers started at $(date -u -d @$t0 +%T) UTC; reload every ${RE}s for ${DUR}s"
n=0; while [ $(date +%s) -lt $((t0 + DUR)) ]; do sleep $RE; systemctl --user daemon-reload; n=$((n+1)); done
echo "real daemon-reloads: $n"
for u in $units; do
  echo "-- $u.service (journal):"
  journalctl --user -u $u.service --since @$t0 -o short-unix --no-pager | python3 -c "
import sys
t0 = $t0
st = [float(l.split()[0]) for l in sys.stdin if 'Starting' in l]
print('   checks started: %d; seconds after timer start: %s' % (len(st), [round(x - t0, 1) for x in st]))
g = [round(b - a, 1) for a, b in zip(st, st[1:])]
print('   gaps: %s; MAX_GAP=%s FIRST=%s' % (g, max(g) if g else None, round(st[0] - t0, 1) if st else None))"
  systemctl --user stop $u.timer $u.service 2>/dev/null; rm -f $SD/$u.timer $SD/$u.service
done
systemctl --user daemon-reload; for u in $units; do systemctl --user reset-failed $u.timer $u.service 2>/dev/null; done
echo "cleanup: $(systemctl --user list-units --all --no-legend 'agent-loop-liveness-p12tpl*' | wc -l) units left"
