#!/bin/bash
# Pure unit tests of plans/rung-eval.sh on synthetic send logs (no host effects).
. /var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership/plans/rung-eval.sh
T=$(mktemp -d); n=0; bad=0; DL=$(date -u -d 2026-09-24T12:00:00Z +%s)
t() { n=$((n+1)); rung_eval "$2" "$T/log" D1 INC1 $DL; r=$?; [ $r = $3 ] && echo "ok   $1" || { bad=$((bad+1)); echo "FAIL $1 (rc $r want $3)"; }; }
row() { printf '%s\tcampaign4\t%s\t%s\t%s\t100\t-\t%s\n' "$1" "$2" "$2" "$3" "$4" > "$T/log"; }
row 2026-09-24T12:00:05Z D1 started "[agent-loop] DECISION OVERDUE INC1: package"; t "started, incident, after deadline" "sent 12:00:05" 0
row 2026-09-24T12:00:05Z D1 "queued (busy)" "[agent-loop] DECISION OVERDUE INC1: package"; t "queued (rc 3) accepted" "sent 12:00:05" 0
row 2026-09-24T12:00:05Z D1 started "[agent-loop] DECISION OVERDUE INC1: package"; t "NEG no rung in DB (null)" "" 1
row 2026-09-24T12:00:05Z D1 started "[agent-loop] DECISION OVERDUE INC1: package"; t "NEG DB rung failed" "failed 12:00:05: x" 1
row 2026-09-24T12:00:05Z D1 started "P13 fixture priming, run r1"; t "NEG unrelated wake to the seat" "sent 12:00:05" 1
row 2026-09-24T12:00:05Z D1 started "[agent-loop] DECISION OVERDUE INC2: other"; t "NEG other incident" "sent 12:00:05" 1
row 2026-09-24T12:00:05Z D2 started "[agent-loop] DECISION OVERDUE INC1: package"; t "NEG other seat" "sent 12:00:05" 1
row 2026-09-24T11:59:00Z D1 started "[agent-loop] DECISION OVERDUE INC1: package"; t "NEG before the deadline" "sent 12:00:05" 1
row 2026-09-24T12:00:05Z D1 failed "[agent-loop] DECISION OVERDUE INC1: package"; t "NEG failed transport" "sent 12:00:05" 1
echo "rung-eval: $n checks, $bad wrong"; rm -r "$T"; [ $bad -eq 0 ]
