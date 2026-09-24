#!/bin/bash
# P13-repair-1 STOPPED-RUN witness (pre-registered before its run). run is started only to bring Q1/Q2 to the
# decision step and is then KILLED (not running) for the whole ladder: only the real calendar decision timer
# (decision-check) and the outside check (agent-loop liveness, own process every 5 s) act. Private candidate
# escalation-watch + escalation-resolve (repo adapters/, hashes recorded) replace the installed watcher in the
# sandbox; notify-claude/escalations are the installed ones, copied. Responder proof: --cap-file from the notice.
# Q1: ladder -> Claude rung -> forged/literal/wrong acks refused -> real ack (60 s) -> expiry -> same-key re-raise
#     -> NO decision -> private watcher PAGES (recurrence unresolved).
# Q2: same up to the re-raise -> director decides -> resolution record -> private watcher: NO page for Q2.
# Original header follows.
# - agent-loop (release binary) in its own processes; REAL systemd-run calendar timers for the decision deadline
#   (isolated unit names agent-loop-<project>-*), daemon-reload and a run restart during the wait.
# - The fleet's ACTUAL escalation scripts (notify-claude, escalations, escalation-watch), copied byte-for-byte into
#   a sandbox HOME (hashes recorded) and run with HOME=sandbox: the real ledger, pager and fleet are never touched.
#   The pager ("ticket") is a stub that records the page: Brian is never paged. notify-claude may still reach a
#   live chat listener with this clearly labelled fixture text.
# Q1: overdue -> director -> duty -> Claude rung (durable ledger record) -> actual decision -> ledger records acked ->
#     escalation-watch: NO page.   Q2: overdue -> Claude rung -> Claude acks the ledger AND decision-ack (90 s) ->
#     expiry -> re-raise with the SAME key -> escalation-watch pages "RECURRED AFTER AN ACK" to the stub.
# Usage: decision-witness.sh BINARY OUTDIR
set -u
A_=$1; OUT=$2; mkdir -p $OUT
mkdir -p ~/.cache/p13w; SB=$(mktemp -d ~/.cache/p13w/w-XXXX); H=$SB/home; S=$SB/stubs; X=$SB/fx
mkdir -p $H/.config/agent-deck $H/.local/share/agent-deck $S $X/stream $X/art $X/claims
P=p13w$(date +%H%M%S); ts() { date -u +%FT%T.%3NZ; }; log() { echo "$(ts) $*" | tee -a $OUT/witness.log; }
for f in notify-claude escalations; do cp -p ~/.config/agent-deck/$f $H/.config/agent-deck/; done; ADP=$(dirname $A_)/../adapters; [ -d $ADP ] || ADP=$HOME/projects/agent-loop-p13/adapters; cp -p $ADP/escalation-watch $ADP/escalation-resolve $H/.config/agent-deck/
sha256sum ~/.config/agent-deck/{notify-claude,escalations} $ADP/escalation-watch $ADP/escalation-resolve $H/.config/agent-deck/{notify-claude,escalations,escalation-watch,escalation-resolve} > $OUT/pinned-scripts.sha256
printf '#!/bin/sh\necho "$(date -u +%%FT%%TZ) PAGE: $*" >> %s/pages.log\ncat >> %s/pages.log\n' $SB $SB > $H/.config/agent-deck/ticket; chmod +x $H/.config/agent-deck/ticket
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
printf '#!/bin/sh\necho "$(date -u +%%FT%%T.%%3NZ) $1 $(printf %%s "$2" | head -c 140)" >> %s/wake.log\necho "wake: $1 -> started"\n' $SB > $S/wake
chmod +x $S/*
NC="$H/.config/agent-deck/notify-claude"; ESC="$H/.config/agent-deck/escalations"
cat > $X/fx.json <<EOF
{"project": "$P", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "$P.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_", "agent_deck": "$S/agent-deck",
 "decision_deadline_s": 60, "decision_policy": "", "decision_responders": ["claude"],
 "decision_ladder": [{"after_s": 0, "seat": "fx-director"}, {"after_s": 20, "seat": "fx-duty"},
   {"after_s": 40, "exec": ["/usr/bin/env", "HOME=$H", "$NC", "decision"], "ledger": "$H/.local/share/agent-deck/escalations.jsonl",
    "ledger_kind": "decision", "resolve_cmd": ["/usr/bin/env", "HOME=$H", "$H/.config/agent-deck/escalation-resolve"]}]}
EOF
C="--config $X/fx.json"; { echo "binary $(sha256sum $A_)"; echo "project $P sandbox $SB"; echo "host_utc_start $(ts)"; } > $OUT/env.txt
end() { f=$X/stream/$1.jsonl; i=i$(date +%s%3N); printf '{"t": "start", "item": "%s"}\n{"t": "end", "item": "%s"}\n' $i $i >> $f; }
step() { $A_ status $C --json 2>/dev/null | python -c "import json,sys; print([p['step'] for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0])" 2>/dev/null; }
waitstep() { for i in $(seq 1 60); do [ "$(step $1)" = "$2" ] && return 0; sleep 1; done; log "TIMEOUT waiting $1 step $2 (at $(step $1))"; return 1; }
dec() { $A_ status $C --json 2>/dev/null | python -c "import json,sys; print(json.dumps([p.get('decision') for p in json.load(sys.stdin)['packages'] if p['qid']=='$1'][0]))"; }
$A_ run $C --every 2s > $SB/run1.out 2>&1 & RUN=$!; log "run pid $RUN"
todecision() { # QID
  $A_ dispatch $C --qid $1 --worker fx-worker --verifier fx-verifier --task t --verify-task v --duration 1h --verify-window 1h >>$SB/cli.out 2>&1
  waitstep $1 worker; sleep 2.5; echo o > $X/art/o-$1; $A_ claim $C --qid $1 --step worker --outcome completed --artifact o=o-$1 >>$SB/cli.out 2>&1; end W1
  waitstep $1 verify; sleep 2.5; echo ok > $X/art/r-$1; $A_ claim $C --qid $1 --step verify --outcome completed --artifact r=r-$1 >>$SB/cli.out 2>&1; end V1
  waitstep $1 decision && log "$1 entered decision: $(dec $1)"; }
todecision Q1
log "timers: $(systemctl --user list-timers --all --no-legend "agent-loop-$P-*" | awk '{print $NF}' | tr '\n' ' ')"
log "daemon-reload during the wait"; systemctl --user daemon-reload
todecision Q2
log "STOP: run killed; from here only the decision timer and the outside check act"; kill $RUN; wait $RUN 2>/dev/null; RUN=
( while :; do $A_ liveness $C >> $SB/liveness.out 2>&1; echo "$(ts) liveness rc=$?" >> $SB/liveness.log; sleep 5; done ) & CHK=$!
log "outside check loop pid $CHK; run pid: none (ps: $(ps -eo args | grep -c "[a]gent-loop run $C"))"
for q in Q1 Q2; do for i in $(seq 1 150); do dec $q | grep -q '"2": "sent' && break; sleep 1; done; log "$q after the ladder: $(dec $q)"; done
cap() { ls $X/fx.db.caps/D-$1-$1-v1.claude; }
log "cap files: $(stat -c '%a %n' $X/fx.db.caps $X/fx.db.caps/* | tr '\n' ' ')"
grep -l "$(cat $(cap Q1))" $X/stream/* $SB/*.out $H/.local/share/agent-deck/escalations.jsonl 2>/dev/null | sed 's/^/SECRET LEAK in /' | tee -a $OUT/witness.log
$A_ decision-ack $C --qid Q1 --by claude --next x --within 60s >>$SB/cli.out 2>&1; log "literal claude without --cap-file rc=$? (want 1)"
echo 0000000000000000000000000000000000000000000000000000000000000000 > $SB/guess; $A_ decision-ack $C --qid Q1 --by claude --cap-file $SB/guess --next x --within 60s >>$SB/cli.out 2>&1; log "guessed capability rc=$? (want 1)"
$A_ decision-ack $C --qid Q1 --by claude --cap-file $(cap Q2) --next x --within 60s >>$SB/cli.out 2>&1; log "Q2's capability on Q1 (cross-incident) rc=$? (want 1)"
$A_ decision-ack $C --qid Q1 --by claude --cap-file $(cap Q1) --next x --within 20m >>$SB/cli.out 2>&1; log "forged deadline 20m rc=$? (want 1)"
for q in Q1 Q2; do
  id=$(python -c "import json;rs=[json.loads(l) for l in open('$H/.local/share/agent-deck/escalations.jsonl') if l.strip()];print([r['id'] for r in rs if 'id' in r and '$q' in r.get('text','')][-1])")
  HOME=$H $ESC --ack $id --note "witness: Claude acknowledges" >>$SB/cli.out 2>&1; log "Claude acked ledger $id ($q)"
  $A_ decision-ack $C --qid $q --by claude --cap-file $(cap $q) --next "witness: chase the director" --within 60s >>$SB/cli.out 2>&1; log "$q decision-ack with capability rc=$? (want 0)"
done
for q in Q1 Q2; do for i in $(seq 1 150); do dec $q | grep -q '"reraised": "sent' && break; sleep 1; done; log "$q after the ack expiry: $(dec $q)"; done
$A_ decision-ack $C --qid Q1 --by claude --cap-file $SB/stale-copy --next x --within 60s >>$SB/cli.out 2>&1
log "Q2: the director decides (actual decision) while run is stopped"; $A_ decide $C --qid Q2 --kind question_answered --ref wit-2 --reason witness >>$SB/cli.out 2>&1; log "Q2 decide rc=$? decision: $(dec Q2)"
sleep 6; kill $CHK; wait $CHK 2>/dev/null
log "private escalation-watch (sandbox HOME, grace 0; page goes to the stub):"
HOME=$H ESCALATION_GRACE_MIN=0 python $H/.config/agent-deck/escalation-watch >> $OUT/escalation-watch.out 2>&1; echo "rc=$?" >> $OUT/escalation-watch.out
cat $OUT/escalation-watch.out | tee -a $OUT/witness.log
cp $SB/wake.log $H/.local/share/agent-deck/escalations.jsonl $SB/cli.out $SB/liveness.log $OUT/ 2>/dev/null; cp $SB/pages.log $OUT/pages.log 2>/dev/null || echo "(no page)" > $OUT/pages.log
$A_ status $C --json > $OUT/status-final.json 2>&1
log "Q1 paged: $(grep -c 'Q1' $OUT/pages.log) lines; Q2 paged: $(grep -c 'Q2' $OUT/pages.log) lines (want Q1 >0, Q2 0)"
# cleanup: the loop's own timers, processes, sandbox (capability files go with it)
for u in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" | awk '{print $1}'); do systemctl --user stop $u; done
systemctl --user reset-failed "agent-loop-$P-*" 2>/dev/null
log "cleanup: $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" | wc -l) units left"; rm -r $SB; log "sandbox removed"
