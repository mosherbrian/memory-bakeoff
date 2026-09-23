#!/bin/bash
# P11-repair-1 offline tests. Registry, agent-deck, systemctl, systemd-run, journalctl are stubs;
# no real seat, unit or global effect. Part A: the driver's real helpers (eval'd unchanged from
# ts() to "# end of helpers"). Part B: the whole driver (a copy with PKG/PLANS/SD redirected to a
# temp dir) for preflight failures, which must stop before any effect. Usage: r1-repair-tests.sh DRIVER
set -u
DRIVER=$1; X=$(mktemp -d /tmp/p11-r1-XXXX); STUB=$X/stub; mkdir -p $STUB $X/ev $X/root/tasks $X/plans/tasks $X/sd
export STUB
cat > $STUB/agent-deck <<'EOF'
#!/bin/bash
R=$STUB/registry.json
if [ "$1 $2" = "list --json" ]; then echo "$(date +%s.%N) READ agent-deck prof=${AGENTDECK_PROFILE:-} :: $*" >> $STUB/effects.log
  python3 -c "import json,os; print(json.dumps([r for r in json.load(open('$R')) if r.get('profile')==os.environ.get('AGENTDECK_PROFILE')]))"; exit 0; fi
echo "$(date +%s.%N) EFFECT agent-deck prof=${AGENTDECK_PROFILE:-} :: $*" >> $STUB/effects.log
case "$1 $2" in
  "session stop") rc=$(cat $STUB/stop_rc 2>/dev/null || echo 0); [ "$rc" = 0 ] && [ "$(cat $STUB/stop_effect 2>/dev/null || echo 1)" = 1 ] && python3 -c "
import json; d=json.load(open('$R')); [r.update(status='stopped') for r in d if r['id']=='$3']; json.dump(d,open('$R','w'))"; exit $rc;;
  "session remove") rc=$(cat $STUB/remove_rc 2>/dev/null || echo 0); [ "$rc" = 0 ] && python3 -c "
import json; d=json.load(open('$R')); json.dump([r for r in d if r['id']!='$3'],open('$R','w'))"; exit $rc;;
esac; exit 0
EOF
for t in systemctl systemd-run journalctl; do printf '#!/bin/bash\necho "$(date +%%s.%%N) EFFECT %s :: $*" >> $STUB/effects.log\ncase "$*" in *is-active*) echo inactive;; esac\nexit 0\n' $t > $STUB/$t; done
chmod +x $STUB/*; export PATH=$STUB:$PATH
reg() { # four fixtures in profile fxprof (optionally modified by python expr on d)
  python3 -c "
import json; d=[dict(id=i,title=t,profile='fxprof',status='idle',archived=False) for i,t in [('W1','fxw'),('V1','fxv'),('D1','fxd'),('U1','fxu')]]
${1:-pass}
json.dump(d,open('$STUB/registry.json','w'))"; }
ok=0; bad=0
chk() { if [ "$2" = "$3" ]; then echo "PASS  $1: '$2'"; ok=$((ok+1)); else echo "FAIL  $1: got '$2' want '$3'"; bad=$((bad+1)); fi; }
echo "== driver $(sha256sum "$DRIVER" | cut -c1-16) workdir $X"
# ---------------- Part A: real helpers
A_ENV() { EV=$X/ev; ROOT=$X/root; P=fx; DRY=0; U=agent-loop-fx.service; LU=agent-loop-liveness-fx; SD=$X/sd; PLANS=$X/plans; A=/bin/true; C=""
  PROFILE=fxprof; export AGENTDECK_PROFILE=fxprof; W_ID=W1; W_NAME=fxw; V_ID=V1; V_NAME=fxv; D_ID=D1; D_NAME=fxd; U_ID=U1; U_NAME=fxu
  WALL=p11live-wallstop-T; LIVE_DEADLINE=2026-09-23T16:00:00Z; DL_EPOCH=$(date -u -d $LIVE_DEADLINE +%s); unset TEARDOWN; : > $EV/results.tsv; : > $STUB/effects.log; rm -rf $EV/cleanup.lock; }
H=$(sed -n '/^ts()/,/^# end of helpers/p' "$DRIVER")
echo "-- deadline guard"
for c in "before:-1:0:ran" "equal:0:3:absent" "after:5:3:absent"; do IFS=: read name off wantrc wantf <<<"$c"
  r=$( A_ENV; eval "$H"; _now() { echo $(( DL_EPOCH + off )); }; rm -f $X/sentinel; run touch $X/sentinel >/dev/null; echo "rc=$?" ); rc=$?
  [ -e $X/sentinel ] && f=ran || f=absent
  chk "guard $name deadline: exit" "$rc" "$wantrc"; chk "guard $name deadline: command" "$f" "$wantf"
  [ "$name" != before ] && chk "guard $name: DEADLINE INCOMPLETE row" "$(cut -f1,2 $X/ev/results.tsv | tr '\t' ' ')" "DEADLINE INCOMPLETE"
done
( A_ENV; eval "$H"; _now() { echo $(( DL_EPOCH + 1 )); }; printf 'x {QID}\n' > $X/plans/tasks/t.md; task t.md Q1 >/dev/null ); chk "task() refused after deadline: no task file" "$([ -e $X/root/tasks/Q1-t.md ] && echo written || echo absent)" absent
reg; r=$( A_ENV; eval "$H"; _now() { echo $(( DL_EPOCH + 100 )); }; cleanup >/dev/null; echo "rc=$?" )
chk "expired cleanup runs (teardown not refused)" "$r" "rc=0"
chk "expired cleanup: no DEADLINE row" "$(grep -c DEADLINE $X/ev/results.tsv)" 0
chk "expired cleanup: fixtures removed" "$(python3 -c "import json;print(len(json.load(open('$STUB/registry.json'))))")" 0
chk "expired cleanup: driver.log says cleanup done" "$(tail -1 $X/ev/driver.log | grep -o 'cleanup done')" "cleanup done"
echo "-- registry_check"
for c in "valid::0" "title:d[0]['title']='other':1" "missing:del d[3]:1" "duplicate:d.append(dict(d[1])):1" "archived:d[2]['archived']=True:1" "wrongprofile:[r.update(profile='campaign4') for r in d]:1"; do
  IFS=: read name expr want <<<"$c"; reg "$expr"
  m=$( A_ENV; eval "$H"; registry_check ); rc=$?
  chk "registry $name rc" "$rc" "$want"; echo "      ($m)"
done
echo "-- stop_seat (L4b onset precondition)"
for c in "stop ok, registry stopped:0:1:0" "stop command fails:1:1:1" "stop ok, registry still idle:0:0:1"; do IFS=: read name src eff want <<<"$c"
  reg; echo $src > $STUB/stop_rc; echo $eff > $STUB/stop_effect
  ( A_ENV; eval "$H"; stop_seat U1 >/dev/null ); chk "stop_seat: $name" "$?" "$want"; done
rm -f $STUB/stop_rc $STUB/stop_effect
echo "-- cleanup outcome checked"
reg; echo 1 > $STUB/remove_rc; r=$( A_ENV; eval "$H"; cleanup >/dev/null; echo "rc=$?" )
chk "cleanup with failing remove: rc" "$r" "rc=1"; chk "cleanup with failing remove: CLEANUP FAIL row" "$(cut -f1,2 $X/ev/results.tsv | tr '\t' ' ')" "CLEANUP FAIL"
chk "cleanup with failing remove: no 'cleanup done'" "$(tail -1 $X/ev/driver.log | grep -c 'cleanup done')" 0
echo "      ($(cut -f4 $X/ev/results.tsv))"; rm -f $STUB/remove_rc
echo "-- L6 timing (explicit class)"
for c in "on time|2026-09-23T16:00:00Z|2026-09-23T16:00:20Z|2026-09-23T16:00:21Z|2026-09-23T16:00:21Z|PASS" \
         "timer 45 s late|2026-09-23T16:00:00Z|2026-09-23T16:00:45Z|2026-09-23T16:00:46Z|2026-09-23T16:00:46Z|FAIL" \
         "detection 30 s exactly|2026-09-23T16:00:00Z|2026-09-23T16:00:30Z|2026-09-23T16:00:31Z|2026-09-23T16:00:31Z|PASS" \
         "detection 31 s|2026-09-23T16:00:00Z|2026-09-23T16:00:31Z|2026-09-23T16:00:32Z|2026-09-23T16:00:32Z|FAIL" \
         "owned 95 s|2026-09-23T16:00:00Z|2026-09-23T16:00:10Z|2026-09-23T16:01:35Z|2026-09-23T16:00:11Z|FAIL" \
         "interrupt before deadline|2026-09-23T16:00:00Z|2026-09-23T15:59:50Z|2026-09-23T16:00:01Z|2026-09-23T16:00:01Z|FAIL" \
         "no director wake|2026-09-23T16:00:00Z|2026-09-23T16:00:10Z|2026-09-23T16:00:11Z||INCOMPLETE" \
         "no deadline recorded||2026-09-23T16:00:10Z|2026-09-23T16:00:11Z|2026-09-23T16:00:11Z|INCOMPLETE"; do
  IFS='|' read name dl it cs ds want <<<"$c"
  r=$( A_ENV; eval "$H"; l6_eval "$dl" "$it" "$cs" "$ds" ); chk "L6 $name" "${r%% *}" "$want"; echo "      ($r)"; done
# ---------------- Part B: whole driver, preflight failures stop before any effect
echo "-- whole driver preflight"
sed -e "s#^SD=.*#SD=$X/sd#" -e "s#^PLANS=.*#PLANS=$X/plans#" -e "s#^PKG=.*#PKG=$X/pkg#" "$DRIVER" > $X/driver-copy.sh
inputs() { cat > $X/in.env <<EOF
RUN=T$1
ROOT=$X/root-$1
LIVE_DEADLINE=${3:-$(date -u -d '+10 min' +%Y-%m-%dT%H:%M:%SZ)}
PROFILE=${2:-fxprof}
WAKE=$STUB/wake
STREAMS=$X/streams
BIN_SRC=/bin/true
BIN_SHA=x
UNITS_SRC=$X/units
W_NAME=fxw
W_ID=W1
V_NAME=fxv
V_ID=${4:-V1}
D_NAME=fxd
D_ID=D1
U_NAME=fxu
U_ID=U1
EOF
}
n=0
for c in "wrong profile|campaign4||||3|SETUP FAIL" "title mismatch|fxprof|||d[0]['title']='x'|3|SETUP FAIL" "duplicate id|fxprof||W1||2|" "bad deadline|fxprof|not-a-time|||2|" "past deadline|fxprof|2026-09-23T00:00:00Z|||3|SETUP INCOMPLETE" "scope not created (stub systemd-run)|fxprof||||3|SETUP FAIL"; do
  IFS='|' read name prof dl vid expr wantrc wantrow <<<"$c"
  reg "${expr:-pass}"; : > $STUB/effects.log; n=$((n+1)); E=$X/evB-$n; mkdir -p $E
  inputs "$n" "$prof" "$dl" "${vid:-V1}"
  EV_DIR=$E bash $X/driver-copy.sh $X/in.env > $E/out.txt 2>&1; rc=$?
  chk "driver $name: exit" "$rc" "$wantrc"
  chk "driver $name: row" "$(cut -f1,2 $E/results.tsv 2>/dev/null | tr '\t' ' ')" "$wantrow"
  want_eff=0; case "$name" in scope*) want_eff=1;; esac   # the one refused scope-creation attempt
  chk "driver $name: effects before exit" "$(grep -c EFFECT $STUB/effects.log)" $want_eff
  echo "      ($(tail -1 $E/out.txt | cut -c1-150))"
done
echo "== $ok PASS, $bad FAIL"; [ $bad -eq 0 ]
