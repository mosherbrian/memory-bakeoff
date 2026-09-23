#!/bin/bash
# P12-bounded-deadline-1: busy callback -> due marker -> settled by the lock holder before release.
# Real separate processes on one ledger. A worker claim and turn end are ready when the step's deadline
# passes. Process A (`run --once`) is frozen by a barrier after it loaded the ledger: the package declares an
# input that is a named pipe, which A reads (input-change check) before its hand-off. Process B (the
# deadline callback, exact armed argv) runs; then A is released (same pipe content, so no input change).
# MODE same: the pipe gives the registered content (A's hand-off then fails on the passed deadline).
# MODE changed: the pipe gives other content, so A takes its blocked() path (E_INPUT_CHANGED) and writes the
# package from its view: the stale whole-record write that can drop the timeout.
# Stub wake/agent-deck/systemctl/systemd-run; no real unit or seat. Usage: race-callback-vs-run.sh BINARY same|changed
set -u
A_=$1; MODE=${2:-same}; X=$(mktemp -d /tmp/p12-race-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
cat > $S/agent-deck <<EOF
#!/bin/sh
echo '[{"id": "W1", "title": "fx-worker"}, {"id": "V1", "title": "fx-verifier"}, {"id": "D1", "title": "fx-director"}, {"id": "U1", "title": "fx-duty"}]'
EOF
cat > $S/wake <<EOF
#!/bin/sh
echo "\$(date -u +%T.%N | cut -c1-12) \$1 \$(echo "\$2" | tr '\n' ' ' | head -c 90)" >> $X/wake.log
[ "\$2" = "/cancel" ] && { echo "wake: \$1 -> nothing running"; exit 1; }
echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\nexit 0\n' > $S/systemctl; printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "fx.service",
 "seats": {"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_",
 "agent_deck": "$S/agent-deck", "systemctl": "$S/systemctl", "systemd_run": "$S/systemd-run"}
EOF
C="--config $X/fx.json"
echo "== $(sha256sum $A_ | cut -c1-16) mode $MODE workdir $X"
echo gate > $X/art/gate.fifo   # a regular file at dispatch (its hash is registered) ...
$A_ dispatch $C --qid L --worker fx-worker --verifier fx-verifier --task w --verify-task v --duration 5s --verify-window 5m --input gate.fifo > $X/dispatch.out 2>&1; echo "dispatch rc=$? $(head -c 160 $X/dispatch.out)"
$A_ run $C --once >/dev/null 2>&1
echo done > $X/art/o.txt; $A_ claim $C --qid L --step worker --outcome completed --artifact o=o.txt >/dev/null 2>&1
i=i$(date +%s%3N); printf '{"t": "start", "item": "%s"}\n{"t": "end", "item": "%s"}\n' $i $i >> $X/stream/W1.jsonl
rm $X/art/gate.fifo; mkfifo $X/art/gate.fifo   # ... then a pipe with the same content: a read blocks until released
sleep 6   # the deadline passes with the claim and turn end ready
cb=$(head -1 $X/systemd-run.log | grep -o -- "timer-callback.*")
$A_ run $C --once > $X/a.out 2>&1 & PA=$!
sleep 1.5; kill -0 $PA 2>/dev/null && echo "A (run pass) frozen on the input pipe after loading the ledger at $(date -u +%T.%N | cut -c1-12)" || { echo "A did not block: $(cat $X/a.out)"; exit 1; }
$A_ $cb > $X/b.out 2>&1 & PB=$!
tb=$(date +%s.%N); HOLD=${HOLD:-12}
while kill -0 $PB 2>/dev/null && [ $(python3 -c "print(int($(date +%s.%N)-$tb < $HOLD))") = 1 ]; do sleep 0.1; done
kill -0 $PB 2>/dev/null && echo "B still running after ${HOLD}s" || echo "B (callback) exited after $(python3 -c "print(round($(date +%s.%N)-$tb,2))") s while A held the ledger: $(head -c 200 $X/b.out)"
sleep $(python3 -c "print(max(0, $HOLD - ($(date +%s.%N)-$tb)))"); echo "releasing A at $(date -u +%T.%N | cut -c1-12) (A held the lock ${HOLD}s after B started)"
if [ $MODE = same ]; then echo gate > $X/art/gate.fifo; else echo other > $X/art/gate.fifo; fi; wait $PA; echo "A rc=$? $(tail -1 $X/a.out | cut -c1-150)"; wait $PB; echo "B rc=$? $(head -c 150 $X/b.out)"
echo "A output: $(grep -E 'due|settled' $X/a.out | cut -c1-200)"
dl=$(python3 -c "import sqlite3,json; print('see ledger')" 2>/dev/null)
$A_ status $C --json | python3 -c "import json,sys; p=json.load(sys.stdin)['packages'][0]; print('FINAL step=%s phase=%s timeout=%s' % (p['step'], p['phase'], json.dumps(p.get('timeout'))))"
echo "due dir: $(ls $X/fx.db.due 2>&1 | tr '\n' ' ')"
echo "cancels=$(grep -c ' W1 /cancel' $X/wake.log) verifier_dispatches=$(grep -c ' V1 ' $X/wake.log) director_notices=$(grep -c ' D1 ' $X/wake.log)"
sed 's/^/   wake /' $X/wake.log
