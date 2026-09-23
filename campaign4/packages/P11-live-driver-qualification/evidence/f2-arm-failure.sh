#!/bin/bash
# F2 negative: the wall-stop cannot be armed (systemd-run refuses it). Derived from f2-wallstop-witness.sh by one sed.
# Real systemd-run/systemctl ONLY for the driver's own transient units (names contain "live-driver-" /
# "live-wallstop-"); every other effect goes to stubs that log it with the caller's cgroup.
# The driver copy differs from DRIVER only in PKG=, SD= and PLANS= (redirected to the temp dir).
# Usage: f2-wallstop-witness.sh DRIVER WALL_SECONDS OBSERVE_SECONDS
set -u
DRIVER=$1; WALLS=$2; OBS=$3; X=$(mktemp -d /tmp/p11-f2-XXXX); S=$X/stubs; RUN=W$(date +%H%M%S)
mkdir -p $S $X/plans/tasks $X/sd $X/ev
cp "$(dirname "$DRIVER")"/tasks/*.md $X/plans/tasks/
sed -e "s#^SD=.*#SD=$X/sd#" -e "s#^PLANS=.*#PLANS=$X/plans#" -e "s#^PKG=.*#PKG=$X/pkg#" "$DRIVER" > $X/plans/live-driver.sh
diff "$DRIVER" $X/plans/live-driver.sh | grep '^[<>]' | sed 's/^/   redirect: /'
eff() { echo "printf '%s %s cg=%s :: %s\\n' \"\$(date +%s.%N)\" \"$1\" \"\$(cut -d: -f3 /proc/\$\$/cgroup)\" \"\$*\" >> $X/effects.log"; }
cat > $S/systemctl <<EOF
#!/bin/bash
case "\$*" in *live-driver-*|*live-wallstop-*) exec /usr/bin/systemctl "\$@";; esac
$(eff systemctl)
case "\$*" in
  *" show "*) printf 'ActiveState=active\nSubState=running\nResult=success\nNRestarts=0\nInvocationID=0f0f\nMainPID=1\nExecMainStartTimestamp=@1\n';;
  *" start "*) printf '{"last_verdict": {"state": "ok"}, "last_check_at": "x"}' > "\$ROOTX/fx$RUN.db.liveness.json";;
  *is-active*) echo active;;
esac; exit 0
EOF
cat > $S/systemd-run <<EOF
#!/bin/bash
case "\$*" in *live-wallstop-*) echo "stub: wall arm refused" >&2; exit 1;; *live-driver-*) exec /usr/bin/systemd-run "\$@";; esac
$(eff systemd-run); exit 0
EOF
for t in agent-deck journalctl; do printf '#!/bin/bash\n%s\nexit 0\n' "$(eff $t)" > $S/$t; done
printf '#!/bin/bash\n%s\necho "wake: $1 -> started"\n' "$(eff wake)" > $S/wake
printf '#!/bin/bash\n%s\ncase "$1" in expose) echo "{\\"packages\\": []}";; esac\nexit 0\n' "$(eff agent-loop)" > $S/agent-loop
chmod +x $S/*
DL=$(date -u -d "+$WALLS sec" +%Y-%m-%dT%H:%M:%SZ)
cat > $X/inputs.env <<EOF
RUN=$RUN
ROOT=$X/root
LIVE_DEADLINE=$DL
PROFILE=none
WAKE=$S/wake
STREAMS=$X/streams
BIN_SRC=$S/agent-loop
BIN_SHA=$(sha256sum $S/agent-loop | cut -d' ' -f1)
UNITS_SRC=/home/bmosher/projects/agent-loop-releases/agent-loop-1341f0469fba/examples/systemd-unqualified
W_NAME=fxw
W_ID=W1
V_NAME=fxv
V_ID=V1
D_NAME=fxd
D_ID=D1
U_NAME=fxu
U_ID=U1
EOF
echo "== driver $(sha256sum "$DRIVER" | cut -c1-16) run $RUN wall at $DL, workdir $X"
t_start=$(date +%s)
( export PATH=$S:$PATH ROOTX=$X/root EV_DIR=$X/ev; exec /bin/bash $X/plans/live-driver.sh $X/inputs.env ) > $X/driver.out 2>&1 &
DPID=$!
sleep "$OBS"
# the bound: the WALLSTOP row's time (the wall fires <= AccuracySec after the deadline); else the deadline
ws=$(awk -F'\t' '$1=="WALLSTOP"{print $3; exit}' $X/ev/results.tsv 2>/dev/null)
t_wall=$(date -d "${ws:-$DL}" +%s.%N); echo "-- bound used: ${ws:-$DL (no WALLSTOP row)}"
echo "-- after ${OBS}s: driver pid $DPID alive=$(kill -0 $DPID 2>/dev/null && echo yes || echo no)"
echo "-- results.tsv:"; sed 's/^/   /' $X/ev/results.tsv 2>/dev/null
echo "-- effects by the driver's cgroup after the bound (deadline $DL):"
late=$(awk -v w=$t_wall '$1+0 > w+0 && $0 !~ /wallstop/' $X/effects.log)
echo "-- every effect, by cgroup:"; awk '{print $2, $3}' $X/effects.log | sort | uniq -c | sed 's/^/   /' ; echo "${late:-   none}" | sed 's/^/   /' | cut -c1-200
echo "-- cleanup runs: $(grep -c 'cleanup (exact IDs)' $X/ev/driver.log)"
echo "-- scope: $(/usr/bin/systemctl --user is-active p11live-driver-$RUN.scope 2>&1); wall timer: $(/usr/bin/systemctl --user is-active p11live-wallstop-$RUN.timer p10live-wallstop-$RUN.timer 2>&1 | tr '\n' ' ')"
echo "-- sleep children of the driver left: $(pgrep -P $DPID 2>/dev/null | wc -l)"
echo "LATE_EFFECTS=$(echo -n "$late" | grep -c .) WALLSTOP_ROWS=$(grep -c $'^WALLSTOP\tINCOMPLETE' $X/ev/results.tsv 2>/dev/null) CLEANUPS=$(grep -c 'cleanup (exact IDs)' $X/ev/driver.log) DRIVER_ALIVE=$(kill -0 $DPID 2>/dev/null && echo 1 || echo 0)"
# second cleanup (operator or a repeated wall): must do nothing
n0=$(wc -l < $X/effects.log); PATH=$S:$PATH EV_DIR=$X/ev /bin/bash $X/plans/live-driver.sh $X/inputs.env cleanup > $X/cleanup2.out 2>&1
echo "SECOND_CLEANUP_EFFECTS=$(( $(wc -l < $X/effects.log) - n0 )) msg=\"$(grep -o 'cleanup already ran' $X/cleanup2.out | head -1)\""
kill $DPID 2>/dev/null; wait $DPID 2>/dev/null
echo "-- driver.log tail:"; tail -n 4 $X/ev/driver.log | cut -c1-160 | sed "s/^/   /"
echo "WORKDIR=$X"
