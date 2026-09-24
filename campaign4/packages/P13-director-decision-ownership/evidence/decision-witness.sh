#!/bin/bash
# P13-initial-1 real separate-process witness of director decision ownership.
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
for f in notify-claude escalations escalation-watch; do cp -p ~/.config/agent-deck/$f $H/.config/agent-deck/; done
sha256sum ~/.config/agent-deck/{notify-claude,escalations,escalation-watch} $H/.config/agent-deck/{notify-claude,escalations,escalation-watch} > $OUT/pinned-scripts.sha256
printf '#!/bin/sh\necho "$(date -u +%%FT%%TZ) PAGE: $*" >> %s/pages.log\ncat >> %s/pages.log\n' $SB $SB > $H/.config/agent-deck/ticket; chmod +x $H/.config/agent-deck/ticket
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
printf '#!/bin/sh\necho "$(date -u +%%FT%%T.%%3NZ) $1 $(printf %%s "$2" | head -c 140)" >> %s/wake.log\necho "wake: $1 -> started"\n' $SB > $S/wake
chmod +x $S/*
NC="$H/.config/agent-deck/notify-claude"; ESC="$H/.config/agent-deck/escalations"
cat > $X/fx.json <<EOF
{"project": "$P", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "$P.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_", "agent_deck": "$S/agent-deck",
 "decision_deadline_s": 60, "decision_responders": ["claude"],
 "decision_ladder": [{"after_s": 0, "seat": "fx-director"}, {"after_s": 20, "seat": "fx-duty"},
   {"after_s": 40, "exec": ["/usr/bin/env", "HOME=$H", "$NC", "decision"], "ledger": "$H/.local/share/agent-deck/escalations.jsonl",
    "ledger_kind": "decision", "resolve_cmd": ["/usr/bin/env", "HOME=$H", "$ESC", "--ack"]}]}
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
log "restart run during the wait"; kill $RUN; wait $RUN 2>/dev/null; $A_ run $C --every 2s > $SB/run2.out 2>&1 & RUN=$!; log "run pid $RUN"
# wait for Q1's external rung (deadline + 40 s) and its durable record
for i in $(seq 1 150); do dec Q1 | grep -q '"2": "sent' && break; sleep 1; done; log "Q1 after the ladder: $(dec Q1)"
log "Q1: the director decides (actual decision)"; $A_ decide $C --qid Q1 --kind question_answered --ref wit-1 --reason witness >>$SB/cli.out 2>&1; log "Q1 decide rc=$? decision: $(dec Q1)"
# Q2: Claude responds (ledger ack + loop ack, 90 s), then the ack expires unanswered
for i in $(seq 1 150); do dec Q2 | grep -q '"2": "sent' && break; sleep 1; done; log "Q2 after the ladder: $(dec Q2)"
id=$(python -c "import json;rs=[json.loads(l) for l in open('$H/.local/share/agent-deck/escalations.jsonl') if l.strip()];print([r['id'] for r in rs if 'id' in r and 'Q2' in r.get('text','')][-1])")
HOME=$H $ESC --ack $id --note "witness: Claude acknowledges" >>$SB/cli.out 2>&1; log "Claude acked ledger $id"
$A_ decision-ack $C --qid Q2 --by claude --next "witness: will chase the director" --within 90s >>$SB/cli.out 2>&1; log "decision-ack rc=$?"
$A_ decision-ack $C --qid Q2 --by mallory --next x --within 60s >>$SB/cli.out 2>&1; log "forged decision-ack rc=$? (want 1)"
$A_ decision-ack $C --qid Q2 --by claude --next renew --within 15m >>$SB/cli.out 2>&1; log "renewal decision-ack rc=$? (want 1)"
for i in $(seq 1 130); do dec Q2 | grep -q '"reraised": "sent' && break; sleep 1; done; log "Q2 after the ack expiry: $(dec Q2)"
log "escalation-watch (actual script, sandbox HOME, grace 0 min for the fixture; the page goes to the stub):"
HOME=$H ESCALATION_GRACE_MIN=0 python $H/.config/agent-deck/escalation-watch >> $OUT/escalation-watch.out 2>&1; echo "rc=$?" >> $OUT/escalation-watch.out
cat $OUT/escalation-watch.out | tee -a $OUT/witness.log
cp $SB/wake.log $H/.local/share/agent-deck/escalations.jsonl $SB/cli.out $OUT/ 2>/dev/null; cp $SB/pages.log $OUT/pages.log 2>/dev/null || echo "(no page)" > $OUT/pages.log
$A_ status $C --json > $OUT/status-final.json 2>&1
# cleanup: the loop's own timers, processes, sandbox
kill $RUN; wait $RUN 2>/dev/null
for u in $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" | awk '{print $1}'); do systemctl --user stop $u; done
systemctl --user reset-failed "agent-loop-$P-*" 2>/dev/null
log "cleanup: $(systemctl --user list-units --all --plain --no-legend "agent-loop-$P-*" | wc -l) units left"; rm -r $SB; log "sandbox removed"
