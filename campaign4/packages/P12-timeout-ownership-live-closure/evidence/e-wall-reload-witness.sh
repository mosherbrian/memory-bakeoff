#!/bin/bash
# E witness: REAL daemon-reloads while the driver is blocked (L1's wait loop), then the wall must fire at
# the deadline and stop the driver and its children. The wall's schedule is read before and after each
# reload. Based on the P11 F2 witness; the reloads and schedule reads are the only additions.
# Real systemd-run/systemctl ONLY for the driver's own transient units (names contain "live-driver-" /
# "live-wallstop-"); every other effect goes to stubs that log it with the caller's cgroup.
# The driver copy differs from DRIVER only in PKG=, SD= and PLANS= (redirected to the temp dir).
# Usage: e-wall-reload-witness.sh DRIVER WALL_SECONDS OBSERVE_SECONDS RELOADS
set -u
DRIVER=$1; WALLS=$2; OBS=$3; NR=${4:-3}; X=$(mktemp -d /tmp/p12-e-XXXX); S=$X/stubs; RUN=W$(date +%H%M%S)
mkdir -p $S $X/plans/tasks $X/sd $X/ev
cp "$(dirname "$DRIVER")"/tasks/*.md $X/plans/tasks/
sed -e "s#^SD=.*#SD=$X/sd#" -e "s#^PLANS=.*#PLANS=$X/plans#" -e "s#^PKG=.*#PKG=$X/pkg#" "$DRIVER" > $X/plans/live-driver.sh
diff "$DRIVER" $X/plans/live-driver.sh | grep '^[<>]' | sed 's/^/   redirect: /'
eff() { echo "printf '%s %s cg=%s prof=%s :: %s\\n' \"\$(date +%s.%N)\" \"$1\" \"\$(cut -d: -f3 /proc/\$\$/cgroup)\" \"\${AGENTDECK_PROFILE:-}\" \"\$*\" >> $X/effects.log"; }
cat > $S/systemctl <<EOF
#!/bin/bash
case "\$*" in *live-driver-*|*live-wallstop-*) exec /usr/bin/systemctl "\$@";; esac
$(eff systemctl)
case "\$*" in
  *" show "*) printf 'ActiveState=active\nSubState=running\nResult=success\nNRestarts=0\nInvocationID=0f0f\nMainPID=1\nExecMainStartTimestamp=@1\n';;
  *" start "*) printf '{"last_verdict": {"state": "ok"}, "last_check_at": "x"}' > "\$ROOTX/fx$RUN.db.liveness.json";;
  *is-active*) echo inactive;;
esac; exit 0
EOF
cat > $S/systemd-run <<EOF
#!/bin/bash
case "\$*" in *live-driver-*|*live-wallstop-*) exec /usr/bin/systemd-run "\$@";; esac
$(eff systemd-run); exit 0
EOF
python3 -c "import json; json.dump([dict(id=i,title=t,profile='fxprof',status='idle',archived=False) for i,t in [('W1','fxw'),('V1','fxv'),('D1','fxd'),('U1','fxu')]], open('$X/registry.json','w'))"
cat > $S/agent-deck <<EOF
#!/bin/bash
# registry stub: list answers only in the declared profile; stop/remove change the registry
if [ "\$1 \$2" = "list --json" ]; then python3 -c "import json,os; print(json.dumps([r for r in json.load(open('$X/registry.json')) if r['profile']==os.environ.get('AGENTDECK_PROFILE')]))"; exit 0; fi
$(eff agent-deck)
case "\$1 \$2" in
  "session stop") python3 -c "import json; d=json.load(open('$X/registry.json')); [r.update(status='stopped') for r in d if r['id']=='\$3']; json.dump(d,open('$X/registry.json','w'))";;
  "session remove") python3 -c "import json; d=json.load(open('$X/registry.json')); json.dump([r for r in d if r['id']!='\$3'],open('$X/registry.json','w'))";;
esac; exit 0
EOF
for t in journalctl; do printf '#!/bin/bash\n%s\nexit 0\n' "$(eff $t)" > $S/$t; done
printf '#!/bin/bash\n%s\necho "wake: $1 -> started"\n' "$(eff wake)" > $S/wake
printf '#!/bin/bash\n%s\ncase "$1" in expose) echo "{\\"packages\\": []}";; esac\nexit 0\n' "$(eff agent-loop)" > $S/agent-loop
chmod +x $S/*
DL=$(date -u -d "+$WALLS sec" +%Y-%m-%dT%H:%M:%SZ)
cat > $X/inputs.env <<EOF
RUN=$RUN
ROOT=$X/root
LIVE_DEADLINE=$DL
PROFILE=fxprof
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
sleep 6
WU=$(/usr/bin/systemctl --user list-units --all --plain --no-legend "p1*live-wallstop-$RUN.timer" | awk '{print $1}')
ws() { echo "$1 $(date -u +%T.%3N): $(/usr/bin/systemctl --user show "$WU" -p NextElapseUSecRealtime -p NextElapseUSecMonotonic -p TimersMonotonic -p TimersCalendar --timestamp=unix 2>&1 | tr '\n' ' ')"; }
echo "-- wall unit $WU (deadline $DL = @$(date -d "$DL" +%s))"; ws "   before reloads"
gap=$(( (WALLS - 10) / NR )); [ $gap -lt 2 ] && gap=2
for i in $(seq 1 $NR); do sleep $gap; /usr/bin/systemctl --user daemon-reload; echo "   REAL daemon-reload $i rc=$? at $(date -u +%T.%3N)"; ws "   after reload $i"; done
while [ $(date +%s) -lt $(( t_start + OBS )) ]; do sleep 1; done
# the bound: the WALLSTOP row's time (the wall fires <= AccuracySec after the deadline); else the deadline
ws=$(awk -F'\t' '$1=="WALLSTOP"{print $3; exit}' $X/ev/results.tsv 2>/dev/null)
t_wall=$(date -d "${ws:-$DL}" +%s.%N); echo "-- bound used: ${ws:-$DL (no WALLSTOP row)}"
echo "-- after ${OBS}s: driver pid $DPID alive=$(kill -0 $DPID 2>/dev/null && echo yes || echo no)"
echo "-- results.tsv:"; sed 's/^/   /' $X/ev/results.tsv 2>/dev/null
echo "-- effects by the driver's cgroup after the bound (deadline $DL):"
late=$(awk -v w=$t_wall '$1+0 > w+0 && $0 !~ /wallstop/' $X/effects.log)
echo "-- every effect, by cgroup:"; awk '{print $2, $3}' $X/effects.log | sort | uniq -c | sed 's/^/   /' ; echo "${late:-   none}" | sed 's/^/   /' | cut -c1-200
t_dl=$(date -d "$DL" +%s)
echo "LATE_FROM_DEADLINE=$(awk -v w=$t_dl '$1+0 >= w+0 && $0 !~ /wallstop/' $X/effects.log | grep -c .) (driver-scope effects at or after the authorized deadline $DL)"
echo "-- cleanup runs: $(grep -c 'cleanup (exact IDs)' $X/ev/driver.log)"
echo "-- scope: $(/usr/bin/systemctl --user is-active p11live-driver-$RUN.scope 2>&1); wall timer: $(/usr/bin/systemctl --user is-active p11live-wallstop-$RUN.timer p10live-wallstop-$RUN.timer 2>&1 | tr '\n' ' ')"
echo "-- sleep children of the driver left: $(pgrep -P $DPID 2>/dev/null | wc -l)"
echo "LATE_EFFECTS=$(echo -n "$late" | grep -c .) WALLSTOP_ROWS=$(grep -c $'^WALLSTOP\tINCOMPLETE' $X/ev/results.tsv 2>/dev/null) CLEANUPS=$(grep -c 'cleanup (exact IDs)' $X/ev/driver.log) DRIVER_ALIVE=$(kill -0 $DPID 2>/dev/null && echo 1 || echo 0)"
# second cleanup (operator or a repeated wall): must do nothing
n0=$(wc -l < $X/effects.log); PATH=$S:$PATH EV_DIR=$X/ev /bin/bash $X/plans/live-driver.sh $X/inputs.env cleanup > $X/cleanup2.out 2>&1
echo "SECOND_CLEANUP_EFFECTS=$(( $(wc -l < $X/effects.log) - n0 )) msg=\"$(grep -o 'cleanup already ran' $X/cleanup2.out | head -1)\""
kill $DPID 2>/dev/null; wait $DPID 2>/dev/null
echo "-- wall-side agent-deck calls and their profile:"; grep 'wallstop' $X/effects.log | grep agent-deck | sed -E 's/.*(prof=[^ ]*) :: /   \1 :: /'
echo "WALL_AGENTDECK_PROFILES=$(grep 'wallstop' $X/effects.log | grep agent-deck | grep -o 'prof=[^ ]*' | sort -u | tr '\n' ' ')"
echo "-- driver.log tail:"; tail -n 4 $X/ev/driver.log | cut -c1-160 | sed "s/^/   /"
echo "WORKDIR=$X"
