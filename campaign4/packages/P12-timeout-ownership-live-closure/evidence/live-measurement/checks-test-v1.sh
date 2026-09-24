#!/bin/bash
# P12-live-measurement-1: old vs new live-driver checks on the IMMUTABLE saved live1 raws (raw/), with a negative
# control for each correction. Pure: no unit, seat or ledger is touched. Usage: checks-test.sh (prints TSV; rc 1 on any FAIL)
set -uo pipefail
H=$(cd "$(dirname "$0")" && pwd); R=$H/raw; . "$H/../../plans/live-checks.sh"; . "$R/onsets.env"
U=agent-loop-fxp12live1.service; J=$R/run-unit-live1.short-unix.journal; JC=$R/run-unit-live1.cat.journal
n=0; bad=0
t() { # NAME WANT GOT: WANT is the expected first word (PASS/FAIL/INCOMPLETE) or rc
  n=$((n+1)); local ok=FAIL; [ "$2" = "$3" ] && ok=ok; [ $ok = ok ] || bad=$((bad+1)); printf '%s\t%s\twant=%s\tgot=%s\n' "$ok" "$1" "$2" "$3"; }
w() { echo "${1%% *}"; }
# window slice of the saved short-unix journal
slice() { awk -v a="$1" -v b="$2" '{ if ($1+0 >= a && $1+0 <= b) print }' "$J"; }

# ---- L3a: old helper failed on the REAL journal (pipefail + grep -q => journalctl SIGPIPE 141); new passes
# the old check exactly as live1 ran it at the restart (--since -3min at T3R), on the host journal of that unit
old=$(set -o pipefail; journalctl --user -u $U --since "@$((T3R-180))" --until "@$T3R" -o cat --no-pager | grep -qi watchdog; echo $?)
t "L3a OLD live1 (pipefail grep -q on the real journal)" 141 "$old"
t "L3a the watchdog line IS in the saved raw" 1 "$(grep -c 'Watchdog timeout' "$J")"
t "L3a NEW live1" PASS "$(w "$(slice $((T3A-90)) $((T3R+5)) | l3a_eval $T3A $T3R)")"
t "L3a NEG stale: onset after the watchdog line" FAIL "$(w "$(slice $((T3A-90)) $((T3R+5)) | l3a_eval $((T3R+1)) $((T3R+60)))")"
t "L3a NEG no watchdog line" FAIL "$(w "$(slice $((T3A-90)) $((T3R+5)) | grep -v 'Watchdog timeout' | l3a_eval $T3A $T3R)")"
t "L3a NEG watchdog line but another result" FAIL "$(w "$(slice $((T3A-90)) $((T3R+5)) | sed "s/result 'watchdog'/result 'exit-code'/" | l3a_eval $T3A $T3R)")"

# ---- L4a / L4b: old required Result=start-limit-hit, which systemd left as exit-code; new proves the loop
t "L4a OLD live1 (Result after the start limit)" "exit-code" "$(slice $T4 $((T4+120)) | grep -q "Start request repeated" && slice $T4 $((T4+120)) | grep -o "Failed with result '[a-z-]*'" | tail -1 | sed "s/.*'\(.*\)'/\1/")"
t "L4a NEW live1 (burst 5)" PASS "$(w "$(slice $T4 $((T4+120)) | start_limit_eval $T4 $U 5)")"
t "L4b NEW live1 (burst 5)" PASS "$(w "$(slice $T4B $((T4B+120)) | start_limit_eval $T4B $U 5)")"
t "L4 NEG single crash (first failure only)" FAIL "$(w "$(slice $T4 $((T4+2)) | start_limit_eval $T4 $U 5)")"
t "L4 NEG stale (onset after the loop)" FAIL "$(w "$(slice $T4 $((T4+120)) | start_limit_eval $((T4+60)) $U 5)")"
t "L4 NEG wrong unit" FAIL "$(w "$(slice $T4 $((T4+120)) | sed "s/$U/agent-loop-other.service/" | start_limit_eval $T4 $U 5)")"
t "L4 NEG no rate-limit refusal" FAIL "$(w "$(slice $T4 $((T4+120)) | grep -v 'Start request repeated' | start_limit_eval $T4 $U 5)")"
t "L4 NEG too few restarts for the burst" FAIL "$(w "$(slice $T4 $((T4+120)) | start_limit_eval $T4 $U 9)")"

# ---- L5 / L6b stop waits: journal exit-64 line of the stop (old polled ExecMainStatus and timed out in live1)
t "L5 NEW live1 exit 64 after the stop" PASS "$(w "$(awk -v a=$T5 -v b=$((T5+60)) '{ if ($1+0>=a && $1+0<=b) print }' "$J" | sed 's/^[^ ]* [^ ]* [^ ]* //' | stop_exit_eval)")"
t "L6b NEW live1 exit 64 after the stop" PASS "$(w "$(awk -v a=$T6B -v b=$((T6B+60)) '{ if ($1+0>=a && $1+0<=b) print }' "$J" | sed 's/^[^ ]* [^ ]* [^ ]* //' | stop_exit_eval)")"
t "L5 NEG no exit line (window before the stop)" FAIL "$(w "$(awk -v a=$((T5-120)) -v b=$((T5-1)) '{ if ($1+0>=a && $1+0<=b) print }' "$J" | stop_exit_eval)")"

# ---- L7c and the recovery waits: healthy = ok|rest checked after the event (live1 L7c ended in rest)
old=$( [ "$(echo 'rest 2026-09-24T01:26:51Z' | cut -d' ' -f1)" = ok ] && echo PASS || echo FAIL )
t "L7c OLD live1 (state_is ok on the idle rest)" FAIL "$old"
healthy_eval $T7 "rest 2026-09-24T01:26:51Z"; t "L7c NEW live1 rest after the onset" 0 $?
healthy_eval $T7 "ok 2026-09-24T01:26:51Z"; t "healthy ok after the event" 0 $?
healthy_eval $T7 "rest 2026-09-24T01:25:00Z"; t "healthy NEG stale verdict (before the event)" 1 $?
for s in crashed unknown hung starting restart-loop PARSE-ERROR; do healthy_eval $T7 "$s 2026-09-24T01:26:51Z"; t "healthy NEG $s" 1 $?; done
healthy_eval $T7 "rest"; t "healthy NEG no checked_at" 1 $?

# ---- L6: argv capture (construction only: this cannot prove a live replay) and replay evaluation
A=/home/bmosher/p12live-p12live1/bin/agent-loop
ARGV=$(sed -e "s/.*\[systemd-run\] //" -e "s/\.$//" "$R/l6-callback-argv-from-journal.txt")
ES="{ path=$A ; argv[]=$ARGV ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }"
g=$(echo "$ES" | l6_argv_eval "$A" L6-p12live1); t "L6 argv from the live1 unit's own argv (ExecStart format of coax-dry)" 0 $?
t "L6 argv is the exact callback" "$ARGV" "$g"
echo "$ES" | l6_argv_eval /other/agent-loop L6-p12live1 >/dev/null; t "L6 argv NEG wrong binary" 1 $?
echo "$ES" | l6_argv_eval "$A" L6b-p12live1 >/dev/null; t "L6 argv NEG wrong qid" 1 $?
echo "" | l6_argv_eval "$A" L6-p12live1 >/dev/null; t "L6 argv NEG unit gone (empty)" 1 $?
t "L6 OLD live1 replay did not run" "not found" "$(grep -o 'not found' "$H/../../live-p12live1/driver.log" | head -1)"
ok='{"decision": "already-handled", "note": "{\"decision\": \"already-handled\"}"}'
t "L6 replay PASS shape" PASS "$(w "$(echo "$ok" | l6_replay_eval 0 5 5 9 9)")"
t "L6 replay NEG rc 1" FAIL "$(w "$(echo 'agent-loop: E_LEDGER_BUSY' | l6_replay_eval 1 5 5 9 9)")"
t "L6 replay NEG interrupted again" FAIL "$(w "$(echo '{"decision": "interrupted", "note": ""}' | l6_replay_eval 0 5 5 9 9)")"
t "L6 replay NEG new /cancel" FAIL "$(w "$(echo "$ok" | l6_replay_eval 0 5 6 9 9)")"
t "L6 replay NEG new director wake" FAIL "$(w "$(echo "$ok" | l6_replay_eval 0 5 5 9 10)")"
t "L6 replay NEG no output" FAIL "$(w "$(printf '' | l6_replay_eval 0 5 5 9 9)")"

echo "TOTAL $n checks, $bad wrong"; [ $bad -eq 0 ]
