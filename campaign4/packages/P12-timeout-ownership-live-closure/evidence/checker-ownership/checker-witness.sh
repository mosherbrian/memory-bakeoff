#!/bin/bash
# P12-checker-ownership-1: real systemd witness of the outside check's failure owner. Isolated user units
# p12test-chk-<pid>-{run,check,failed}.service in ~/.config/systemd/user (removed at the end), a fixture ledger
# under ~/.cache/p12-chk, stub wake/agent-deck, REAL systemctl. No fleet seat, no production unit.
# Usage: checker-witness.sh BINARY OUTDIR
set -u
# The workdir is under HOME: the host systemd user manager cannot see a toolbox /var/tmp.
A_=$1; OUT=$2; mkdir -p $OUT; mkdir -p ~/.cache/p12-chk; X=$(mktemp -d ~/.cache/p12-chk/w-XXXX); S=$X/stubs; mkdir -p $S $X/stream $X/art $X/claims
N=p12test-chk-$$; UD=~/.config/systemd/user; ts() { date -u +%FT%T.%3NZ; }; ep() { date +%s.%N; }
log() { echo "$(ts) $*" | tee -a $OUT/witness.log; }
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-v1\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}, {\"id\": \"U1\", \"title\": \"fx-duty\"}]'" > $S/agent-deck
cat > $S/wake <<EOF
#!/bin/sh
if [ "\$1" = U1 ] && [ -e $X/duty-down ]; then echo "\$(date -u +%FT%T.%3NZ) \$1 REFUSED \$(printf '%s' "\$2" | head -c 150)" >> $X/wake.log; echo "wake: could not reach \$1" >&2; exit 1; fi
echo "\$(date -u +%FT%T.%3NZ) \$1 ok \$(printf '%s' "\$2" | tr '\n' ' ' | head -c 150)" >> $X/wake.log; echo "wake: \$1 -> started"
EOF
printf '#!/bin/sh\necho "$*" >> %s/systemd-run.log\n' $X > $S/systemd-run; chmod +x $S/*
cat > $X/fx.json <<EOF
{"project": "fx", "profile": "none", "wake": "$S/wake", "db": "$X/fx.db", "stream_dir": "$X/stream", "claims_dir": "$X/claims",
 "artifacts_dir": "$X/art", "director": "fx-director", "duty": "fx-duty", "unit": "$N-run.service",
 "seats": {"fx-worker": "W1", "fx-v1": "V1", "fx-director": "D1", "fx-duty": "U1"}, "bin": "$A_",
 "agent_deck": "$S/agent-deck", "systemctl": "systemctl", "systemd_run": "$S/systemd-run"}
EOF
cat > $UD/$N-check.service <<EOF
[Unit]
Description=P12 checker witness check (isolated, no seats)
OnFailure=$N-failed.service
[Service]
Type=oneshot
ExecStart=$A_ liveness --config $X/fx.json
TimeoutStartSec=35
EOF
cat > $UD/$N-failed.service <<EOF
[Unit]
Description=P12 checker witness failure handler (isolated, no seats)
[Service]
Type=oneshot
ExecStart=$A_ checker-failed --config $X/fx.json --unit $N-check.service
TimeoutStartSec=20
EOF
cat > $UD/$N-run.service <<EOF
[Unit]
Description=P12 checker witness run (isolated, no seats)
[Service]
Type=notify
ExecStart=$A_ run --config $X/fx.json --every 2s
WatchdogSec=60
TimeoutStopSec=20
EOF
{ echo "binary $(sha256sum $A_)"; echo "workdir $X units $N-*"; uname -r; systemctl --version | head -1; echo "host_utc_start $(ts)"; cat $UD/$N-check.service $UD/$N-failed.service; } > $OUT/env.txt
systemctl --user daemon-reload; systemctl --user start $N-run.service; sleep 4
log "run: $(systemctl --user show $N-run.service -p ActiveState,MainPID --value | tr '\n' ' ')"
snap() { # label
  log "== $1: incident=$(tr -d '\n ' < $X/fx.db.checker-incident.json 2>/dev/null | head -c 600) pending=$(tr -d '\n ' < $X/fx.db.check-pending.json 2>/dev/null)"; }
runcheck() { # label [stop|kill|none]; starts the check unit, waits for it and for its handler to settle
  local label=$1 how=${2:-none} t0; t0=$(ep)
  systemctl --user reset-failed $N-check.service $N-failed.service 2>/dev/null
  systemctl --user start --no-block $N-check.service; log "$label: check started"
  if [ "$how" != none ]; then until p=$(systemctl --user show $N-check.service -p MainPID --value); [ "${p:-0}" != 0 ]; do sleep 0.05; done
    if [ $how = stop ]; then kill -STOP $p; log "$label: SIGSTOP check pid $p"; else sleep 0.5; kill -9 $p; log "$label: SIGKILL check pid $p"; fi; fi
  while [ "$(systemctl --user show $N-check.service -p ActiveState --value)" = activating ]; do sleep 0.1; done
  log "$label: check ended after $(python -c "print(round($(ep)-$t0,1))") s: $(systemctl --user show $N-check.service -p Result,ExecMainCode,ExecMainStatus --value | tr '\n' ' ')"
  sleep 0.5; while [ "$(systemctl --user show $N-failed.service -p ActiveState --value)" = activating ]; do sleep 0.1; done
  log "$label: handler state $(systemctl --user show $N-failed.service -p ActiveState,Result,ExecMainStatus --value | tr '\n' ' ') after $(python -c "print(round($(ep)-$t0,1))") s"
  snap $label; }
hold() { ( flock -x $X/fx.db.lock sh -c "echo held > $X/held; sleep $1" ) & HP=$!; until [ -e $X/held ]; do sleep 0.05; done; rm -f $X/held; log "ledger lock held by fixture pid $HP for $1 s"; }
runcheck S0-healthy
hold 40; runcheck S1-lock-held-nonzero
( $A_ liveness --config $X/fx.json > $OUT/S2-occupier.out 2>&1 ) & OC=$!; sleep 0.5; log "S2: a manual check occupies the one check place (pid $OC)"
runcheck S2-due-cap-refused; wait $OC; wait $HP
runcheck S3-hung-killed-at-timeout stop
runcheck S4-sigkill kill
runcheck S5-recovery
touch $X/duty-down; log "duty transport now REFUSES"
hold 25; runcheck S6-duty-down-director; wait $HP
rm -f $X/duty-down; runcheck S7-recovery
$A_ stop --config $X/fx.json > $OUT/stop.out 2>&1; sleep 3; log "run stopped intentionally: $(systemctl --user show $N-run.service -p ActiveState --value)"
runcheck S8-stopped-quiet
cp $X/wake.log $OUT/; cp $X/fx.db.checker-incident.json $OUT/final-incident.json 2>/dev/null; ls $X/fx.db.check-pending.json > $OUT/final-pending.txt 2>&1
journalctl --user -u $N-check.service -u $N-failed.service -u $N-run.service --since "@${START:-$(date -d "$(sed -n 's/host_utc_start //p' $OUT/env.txt)" +%s)}" -o short-iso-precise --no-pager > $OUT/journal.txt 2>&1
# exact cleanup
systemctl --user stop $N-run.service $N-check.service $N-failed.service 2>/dev/null
systemctl --user reset-failed $N-run.service $N-check.service $N-failed.service 2>/dev/null
rm -f $UD/$N-check.service $UD/$N-failed.service $UD/$N-run.service; systemctl --user daemon-reload
log "cleanup: units $(systemctl --user list-units --all --plain --no-legend "$N-*" | wc -l) left; unit files $(ls $UD/$N-* 2>/dev/null | wc -l) left"
rm -r $X; log "workdir removed $X"
