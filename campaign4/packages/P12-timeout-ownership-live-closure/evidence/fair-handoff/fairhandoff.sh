#!/bin/bash
# P12-fair-handoff-1 harness (extends P12-realprocess-1 realprocess.sh). Real separate processes on one ledger, frozen binary, stubs only (wake, agent-deck,
# systemctl, systemd-run); no unit, no seat, no fleet. The workload is pre-registered in workload.json (written
# before anything runs). Usage: realprocess.sh BINARY MODE OUTDIR    MODE = drain | crash
#   drain: backlog of 14 accepted due deadlines + ordinary arrivals; measures drain order, latency, SATURATED,
#          yields (run output + heartbeat), lock hand-offs, local (non-subprocess) time inside every hold.
#   crash: the same workload; the run process is SIGKILLed mid-hold while a settlement send is in flight,
#          then a new run process is started on the same ledger; pre/post state is captured.
#   crash2: two successive crashes on ONE notice incident: SIGKILL the holder (any writer) while the director
#          notice deadline-expired:Q is in flight, then SIGKILL the holder of its labelled REPEAT; also SIGKILL
#          one queued waiter and SIGSTOP another for 6 s (stuck waiter), then restart run.
set -u
A_=$1; MODE=$2; OUT=$3; mkdir -p $OUT
X=$(mktemp -d /var/tmp/p12-rp-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
ARRIVE_FROM=${ARRIVE_FROM:-stall}; SLOW_ORDINARY=${SLOW_ORDINARY:-1}
N=14; DUR=45; STALL_LEAD=3; STALL=40; ARRIVE_EVERY=${ARRIVE_EVERY:-5}; ARRIVE_FOR=90; TAIL=150; NOTICE_S=1.0; DISPATCH_S=20; FAIL_EVERY=${FAIL_EVERY:-5}
QUEUED_EVERY=${QUEUED_EVERY:-0}; HANG_EVERY=${HANG_EVERY:-0}; HANG_S=15; FAIL_FIRST_DUTY=${FAIL_FIRST_DUTY:-0}
cat > $OUT/workload.json <<EOF
{"mode": "$MODE", "binary_sha256": "$(sha256sum $A_ | cut -d' ' -f1)", "workdir": "$X",
 "backlog": {"packages": $N, "qids": "B01..B$N", "worker": "fx-worker", "verifiers": ["fx-v1", "fx-v2", "fx-v3"], "duration_s": $DUR,
   "accepted_by": "dispatch with fast transport before any contention; all $N registered before the first deadline"},
 "stalled_holder_fixture": {"what": "flock(1) holds <db>.lock (an external writer that does not release)", "starts": "first deadline - ${STALL_LEAD}s", "holds_s": $STALL,
   "why": "every deadline callback must wait DueWait 8 s, write its marker and give up at DueWindow 22 s, so all $N deadlines become accepted due markers"},
 "ordinary_arrivals": {"every_s": $ARRIVE_EVERY, "for_s": $ARRIVE_FOR, "from": "$ARRIVE_FROM", "slow_dispatch_transport": $SLOW_ORDINARY, "duration": "10m (never due in the window)"},
 "transport": {"cancel": "fast, rc 1 'nothing running'", "notice_s": $NOTICE_S, "notice_fail_every": $FAIL_EVERY, "notice_queued_rc3_every": $QUEUED_EVERY, "notice_hang_every": $HANG_EVERY, "fail_first_duty_notice": $FAIL_FIRST_DUTY, "notice_start_lines": "every notice logs a 'started' line at entry (attempt; interval for the local-time measure)", "hang_s": $HANG_S, "hang_effect": "lands after the sleep (a capped send whose effect still arrives: ambiguous)",
   "dispatch_s": $DISPATCH_S, "dispatch_effect": "logged BEFORE the slow reply, so a capped/killed send has landed (ambiguous delivery)"},
 "run": "run --every 2s, its own process", "callbacks": "each armed deadline fired at its calendar instant in its own process",
 "finite_duration": "stall end + ${TAIL}s", "crash": "crash mode only: SIGKILL run at its first hold after the stall in which due markers exist and a send started by run is in flight; restart 3 s later", "crash2": "crash2 mode only: see the header"}
EOF
export AGENT_LOOP_LOCK_LOG=$X/lock.log
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-v1\"}, {\"id\": \"V2\", \"title\": \"fx-v2\"}, {\"id\": \"V3\", \"title\": \"fx-v3\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
# wake.log: <start> <end|-> <caller pid> <seat> <kind> <outcome> <text>. attempt = a line; effect = outcome ok|landed.
cat > $S/wake <<EOF
#!/bin/sh
t=\$(date +%s.%N); txt=\$(printf '%s' "\$2" | tr '\n' ' ' | head -c 160)
case "\$2" in
  /cancel) echo "\$t \$(date +%s.%N) \$PPID \$1 cancel ok /cancel" >> $X/wake.log; echo "wake: \$1 -> nothing running"; exit 1;;
  '{"kind": "dispatch"'*) [ -e $X/slow ] || { echo "\$t \$(date +%s.%N) \$PPID \$1 dispatch ok \$txt" >> $X/wake.log; echo "wake: \$1 -> started"; exit 0; }
      echo "\$t - \$PPID \$1 dispatch landed \$txt" >> $X/wake.log; sleep $DISPATCH_S
      echo "\$t \$(date +%s.%N) \$PPID \$1 dispatch replied \$txt" >> $X/wake.log;;
  *) echo "\$t - \$PPID \$1 notice started \$txt" >> $X/wake.log
     if [ $FAIL_FIRST_DUTY = 1 ] && [ "\$1" = U1 ] && mkdir $X/dutyfailed 2>/dev/null; then sleep $NOTICE_S; echo "\$t \$(date +%s.%N) \$PPID \$1 notice fail \$txt" >> $X/wake.log; echo "wake: could not reach \$1" >&2; exit 1; fi
     n=\$(flock $X/seq.lock sh -c 'n=\$(( \$(cat $X/seq 2>/dev/null || echo 0) + 1 )); echo \$n > $X/seq; echo \$n'); sleep $NOTICE_S
     if [ $HANG_EVERY -gt 0 ] && [ \$((n % $HANG_EVERY)) -eq 0 ]; then sleep $HANG_S; echo "\$t \$(date +%s.%N) \$PPID \$1 notice late-ok \$txt" >> $X/wake.log; echo "wake: \$1 -> started"; exit 0; fi
     if [ $QUEUED_EVERY -gt 0 ] && [ \$((n % $QUEUED_EVERY)) -eq 0 ]; then echo "\$t \$(date +%s.%N) \$PPID \$1 notice queued \$txt" >> $X/wake.log; echo "wake: \$1 -> queued"; exit 3; fi
     if [ \$((n % $FAIL_EVERY)) -eq 0 ]; then echo "\$t \$(date +%s.%N) \$PPID \$1 notice fail \$txt" >> $X/wake.log; echo "wake: could not reach \$1: [Errno 111] Connection refused" >&2; exit 1; fi
     echo "\$t \$(date +%s.%N) \$PPID \$1 notice ok \$txt" >> $X/wake.log;;
esac
echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\nexit 0\n' > $S/systemctl; printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "fx.service",
 "seats": {"fx-worker": "W1", "fx-v1": "V1", "fx-v2": "V2", "fx-v3": "V3", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"; ts() { date +%s.%N; }
{ echo "== binary $(sha256sum $A_ | cut -c1-16) mode=$MODE workdir=$X"; uname -r; grep -m1 'model name' /proc/cpuinfo; nproc; df -T $X | tail -1; } > $OUT/env.txt
# 1. accept the backlog: dispatch wakes are fast until $X/slow exists (created at the stall start)
t0=$(date +%s)
for i in $(seq -w 1 $N); do v=fx-v$(( (10#$i % 3) + 1 )); ( $A_ dispatch $C --qid B$i --worker fx-worker --verifier $v --task t --verify-task v --duration ${DUR}s --verify-window 5m > $X/dB$i.out 2>&1; echo "B$i rc=$?" >> $X/dispatch-rc.log ) & done
until [ $(grep -c 'timer-callback' $X/systemd-run.log 2>/dev/null || echo 0) -ge $N ]; do sleep 0.2; [ $(( $(date +%s) - t0 )) -gt $((DUR - 8)) ] && break; done
grep -o -- '--on-calendar=[^U]*UTC' $X/systemd-run.log | sed 's/--on-calendar=//' | while read -r a; do date -u -d "$a" +%s; done | sort -n > $X/deadlines
echo "armed deadlines: $(wc -l < $X/deadlines) first=$(head -1 $X/deadlines) last=$(tail -1 $X/deadlines) accepted_at=$(ts)" | tee -a $OUT/env.txt
first=$(head -1 $X/deadlines)
# 2. callbacks at their armed instants, each in its own process
grep 'timer-callback' $X/systemd-run.log | while read -r line; do
  at=$(echo "$line" | grep -o -- '--on-calendar=[^U]*UTC' | sed 's/--on-calendar=//'); ep=$(date -u -d "$at" +%s)
  cb=$(echo "$line" | grep -o -- "timer-callback.*"); q=$(echo "$cb" | grep -o -- '--qid [^ ]*' | cut -d' ' -f2)
  ( while [ $(date +%s) -lt $ep ]; do sleep 0.1; done; s=$(ts); $A_ $cb > $X/cb-$q.out 2>&1; rc=$?; echo "$q deadline=$ep start=$s end=$(ts) rc=$rc" >> $X/callbacks.log ) &
done
# 3. run in its own process
$A_ run $C --every 2s > $X/run1.out 2>&1 & PR=$!; echo $PR > $X/run1.pid
# 4. the stalled holder fixture, then ordinary arrivals from the stall start
while [ $(date +%s) -lt $((first - STALL_LEAD)) ]; do sleep 0.1; done
[ $SLOW_ORDINARY = 1 ] && touch $X/slow   # ordinary dispatches are slow from here on
( flock -x $X/fx.db.lock sh -c "echo \$(date +%s%N) \$\$ acquire fixture >> $X/lock.log; sleep $STALL; echo \$(date +%s%N) \$\$ release fixture >> $X/lock.log" ) & PF=$!
stall_start=$(date +%s); stall_end=$((stall_start + STALL)); stop_at=$((stall_end + TAIL))
( [ $ARRIVE_FROM = end ] && while [ $(date +%s) -lt $stall_end ]; do sleep 0.1; done; a0=$(date +%s); n=0; while [ $(( $(date +%s) - a0 )) -lt $ARRIVE_FOR ]; do n=$((n+1)); ( $A_ dispatch $C --qid O$n --worker fx-worker --verifier fx-v1 --task o --verify-task v --duration 10m --verify-window 5m > $X/dO$n.out 2>&1; echo "O$n rc=$? end=$(ts) $(tail -1 $X/dO$n.out | tr -s " " | cut -c1-120)" >> $X/arrivals.log ) & sleep $ARRIVE_EVERY; done; wait ) & PA=$!
# 5. sampler: due markers present and the heartbeat, every 0.5 s
( while [ $(date +%s) -lt $stop_at ]; do echo "$(ts) queue=$(ls $X/fx.db.queue 2>/dev/null | grep -c '^[0-9]*$') due=$(ls $X/fx.db.due 2>/dev/null | grep -v rejected | tr '\n' ',') pass=$(python - $X/fx.db <<'PY' 2>/dev/null
import sqlite3, sys
try:
    c = sqlite3.connect('file:%s?mode=ro' % sys.argv[1], uri=True, timeout=0.2)
    print(c.execute("select value from driver_kv where key='loop-pass'").fetchone()[0].replace(' ', ''))
except Exception as e: print('unreadable')
PY
)"; sleep 0.5; done > $X/samples.log ) & PS=$!
# 6. crash injection
if [ "$MODE" = crash ]; then
  while [ $(date +%s) -lt $stop_at ]; do
    # a run hold is open and a notice started by run is still in flight (no end line yet)
    if [ $(date +%s) -ge $stall_end ] && tail -1 $X/lock.log | grep -q " $PR acquire run" && [ -n "$(ls $X/fx.db.due 2>/dev/null | grep -v rejected)" ] && ls /proc/$PR/task >/dev/null 2>&1 && pgrep -P $PR -f "$S/wake" >/dev/null; then
      { echo "kill_at=$(ts) run_pid=$PR"; echo "-- lock.log tail"; tail -3 $X/lock.log; echo "-- in-flight children"; pgrep -a -P $PR; echo "-- due markers"; ls -l --time-style=+%s.%N $X/fx.db.due; } > $OUT/crash-pre.txt
      cp $X/fx.db $OUT/crash-pre.db 2>/dev/null; cp $X/wake.log $OUT/crash-pre-wake.log
      kill -9 $PR; break
    fi
    sleep 0.05
  done
  wait $PR 2>/dev/null; echo "run1 exit=$? at $(ts)" >> $OUT/crash-pre.txt; sleep 3
  $A_ run $C --every 2s > $X/run2.out 2>&1 & PR=$!; echo $PR > $X/run2.pid; echo "run2 pid=$PR started=$(ts)" >> $OUT/crash-pre.txt
fi
if [ "$MODE" = crash2 ]; then
  ws() { ps -eo pid,ppid,args | awk -v s="$S/wake" '$3=="/bin/sh" && $4==s {print}'; }
  Q=""; k1=""; k2=""; kw=""; ks=""; r2=""
  while [ $(date +%s) -lt $stop_at ] && { [ -z "$k2" ] || [ -z "$kw" ] || [ -z "$ks" ]; }; do
    if [ -n "$k1" ] && ! kill -0 $PR 2>/dev/null && [ -z "$r2" ]; then r2=1; wait $PR 2>/dev/null; echo "run1 pid=$PR was killed; restarting in 3 s" >> $OUT/crash2.txt; sleep 3; $A_ run $C --every 2s > $X/run2.out 2>&1 & PR=$!; echo "run2 pid=$PR started=$(ts)" >> $OUT/crash2.txt; fi
    if [ -z "$k1" ] && [ $(date +%s) -ge $stall_end ]; then
      l=$(ws | grep ' D1 \[agent-loop\] deadline-expired:B' | head -1)
      if [ -n "$l" ]; then hp=$(echo "$l" | awk '{print $2}'); Q=$(echo "$l" | grep -o 'deadline-expired:B[0-9]*' | cut -d: -f2)
        { echo "kill1_at=$(ts) holder_pid=$hp holder_args=$(tr '\0' ' ' < /proc/$hp/cmdline | cut -c1-80) incident=deadline-expired:$Q"; echo "-- in flight: $l" | cut -c1-200; ls $X/fx.db.due; } >> $OUT/crash2.txt
        kill -9 $hp; k1=$hp; fi
    fi
    if [ -n "$k1" ] && [ -z "$k2" ]; then
      l=$(ws | grep " D1 REPEAT (.*deadline-expired:$Q\." | head -1)
      if [ -n "$l" ]; then hp=$(echo "$l" | awk '{print $2}')
        { echo "kill2_at=$(ts) holder_pid=$hp holder_args=$(tr '\0' ' ' < /proc/$hp/cmdline | cut -c1-80) (holder of the labelled repeat)"; echo "-- in flight: $l" | cut -c1-200; } >> $OUT/crash2.txt
        kill -9 $hp; k2=$hp; fi
    fi
    # one queued waiter killed, one stopped for 6 s (both ordinary dispatches that are not at the head)
    if [ -z "$kw" ] || [ -z "$ks" ]; then
      for e in $(ls $X/fx.db.queue 2>/dev/null | grep '^[0-9]*$' | tail -n +2); do
        wp=$(python -c "import json,sys;print(json.load(open(sys.argv[1]))['pid'])" $X/fx.db.queue/$e 2>/dev/null) || continue
        grep -qa dispatch /proc/$wp/cmdline 2>/dev/null || continue
        if [ -z "$kw" ]; then echo "killwaiter_at=$(ts) pid=$wp entry=$e" >> $OUT/crash2.txt; kill -9 $wp; kw=$wp; break
        elif [ -z "$ks" ] && [ "$wp" != "$kw" ]; then echo "stopwaiter_at=$(ts) pid=$wp entry=$e" >> $OUT/crash2.txt; kill -STOP $wp; ks=$wp; ( sleep 6; kill -CONT $wp; echo "contwaiter_at=$(ts) pid=$wp" >> $OUT/crash2.txt ) & break; fi
      done
    fi
    sleep 0.05
  done
  if [ -z "$r2" ] && ! kill -0 $PR 2>/dev/null; then wait $PR 2>/dev/null; echo "run1 pid=$PR was killed; restarting" >> $OUT/crash2.txt; sleep 3; $A_ run $C --every 2s > $X/run2.out 2>&1 & PR=$!; echo "run2 pid=$PR started=$(ts)" >> $OUT/crash2.txt; fi
  echo "incident=$Q kill1=$k1 kill2=$k2 killed_waiter=$kw stopped_waiter=$ks" >> $OUT/crash2.txt
fi
while [ $(date +%s) -lt $stop_at ]; do sleep 1; done
kill -TERM $PR; wait $PR 2>/dev/null; if [ "$MODE" = crash2 ] && ! grep -q run2 $OUT/crash2.txt 2>/dev/null; then :; fi; wait $PA $PF $PS 2>/dev/null; sleep 2
cp $X/lock.log $X/wake.log $X/samples.log $X/callbacks.log $X/arrivals.log $X/dispatch-rc.log $X/systemd-run.log $X/deadlines $X/run*.out $OUT/ 2>/dev/null
ls -la $X/fx.db.due > $OUT/due-dir-final.txt 2>&1; cp $X/fx.db.due/.saturation-attempts $OUT/ 2>/dev/null; ls -la $X/fx.db.queue $X/fx.db.queue/rejected > $OUT/queue-dir-final.txt 2>&1
python - $X/fx.db > $OUT/notice-records.txt <<'PY2'
import sqlite3, sys
c = sqlite3.connect('file:%s?mode=ro' % sys.argv[1], uri=True)
for k, v in c.execute("select key, value from driver_kv where key like 'notice:%' order by key"): print(k, v)
PY2
$A_ status $C --json > $OUT/status-final.json 2>$OUT/status-final.err
echo "stall_start=$stall_start stall_end=$stall_end stop_at=$stop_at" >> $OUT/env.txt
python $(dirname $0)/analyse.py $OUT > $OUT/analysis.txt 2>&1; echo "analysis rc=$?" >> $OUT/analysis.txt
echo "workdir $X (removed)"; rm -rf $X
