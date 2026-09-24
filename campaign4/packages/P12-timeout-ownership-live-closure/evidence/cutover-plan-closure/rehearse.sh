#!/bin/bash
# P12-cutover-plan-closure-1 offline rehearsal of plans/cutover.sh. Sandbox home (CUT_HOME) + stub PATH
# (systemctl, agent-deck; wake under the sandbox home). No real unit, seat, binary or config is touched.
# Usage: rehearse.sh OUTDIR     prints TSV rows: ok|FAIL name want got
set -u
OUT=$1; mkdir -p "$OUT"; SB=$(mktemp -d /tmp/claude-1000/-var-home-bmosher/09b5ba50-67c7-4535-b27c-5baa3e1c4fa8/scratchpad/cutsb-XXXX)
PLANS=/home/bmosher/memory-bake-off/campaign4/packages/P12-timeout-ownership-live-closure/plans
REL=/home/bmosher/projects/agent-loop-releases/agent-loop-8ad12b86fa82
n=0; bad=0; t() { n=$((n+1)); local o=FAIL; [ "$2" = "$3" ] && o=ok; [ $o = ok ] || bad=$((bad+1)); printf '%s\t%s\twant=%s\tgot=%s\n' "$o" "$1" "$2" "$3"; }
mk() { # NAME: a fresh sandbox home + fake release (copy) + stubs; prints the inputs file
  local h=$SB/$1; mkdir -p $h/stub $h/home/.local/bin $h/home/.config/agent-deck $h/home/.config/systemd/user $h/rel/bin
  cp $REL/bin/agent-loop $h/rel/bin/; cp -r $REL/examples $h/rel/
  cp $REL/bin/agent-loop $h/home/.local/bin/agent-loop   # "current" installed binary
  printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"a79067ca-1790000758\", \"title\": \"kiln\"}, {\"id\": \"493c0317-1790000758\", \"title\": \"corvid\"}, {\"id\": \"0c933c75-1790000758\", \"title\": \"tern\"}, {\"id\": \"56513e0e-1790000758\", \"title\": \"cairn\"}]'" > $h/stub/agent-deck
  printf '#!/bin/sh\necho "$*" >> %s/wake.log\necho "wake: $1 -> started"\n' $h > $h/home/.config/agent-deck/wake
  for f in openwork campaign4-watch shadow-watch; do echo x > $h/home/.config/agent-deck/$f; done
  cat > $h/stub/systemctl <<S
#!/bin/bash
echo "\$*" >> $h/systemctl.log
last=\${@: -1}
case " \$* " in
  *" is-active "*) grep -qx "\$last active" $h/active 2>/dev/null && echo active || echo inactive;;
  *" is-enabled "*) grep -qx "\$last enabled" $h/enabled 2>/dev/null && echo enabled || echo disabled;;
  *" disable "*) [ -e $h/fail-disable ] && exit 1; for u in "\$@"; do sed -i "/^\$u /d" $h/active $h/enabled 2>/dev/null; done;;
  *" show "*) echo;;
esac
exit 0
S
  printf '#!/bin/sh\necho "$*" >> %s/systemctl.log\n' $h > $h/stub/systemd-run
  chmod +x $h/stub/* $h/home/.config/agent-deck/wake
  printf 'openwork.timer active\ncoax-dry.timer active\nshadow-watch.timer active\n' > $h/active
  printf 'openwork.timer enabled\ncoax-dry.timer enabled\nshadow-watch.timer enabled\n' > $h/enabled
  sed -e "s|^CUT_RUN=.*|CUT_RUN=reh-$1|" -e "s|^QUALIFIED_BIN=.*|QUALIFIED_BIN=$h/rel/bin/agent-loop|" $PLANS/cutover-inputs.template.env > $h/inputs.env
  echo $h; }
cutover() { local h=$1; shift; CUT_HOME=$h/home EV_DIR=$h/ev PATH=$h/stub:$PATH bash $PLANS/cutover.sh $h/inputs.env "$@" >>$h/out.txt 2>&1; echo $?; }

# P1 capture on the full release: preflight PASS, exact state and kept unit files recorded
h=$(mk p1); t "capture PASS with all 4 units" 0 "$(cutover $h capture)"
t "state.tsv rows (3 timers + campaign4-watch)" 4 "$(wc -l < $h/ev/pre/state.tsv)"
t "captured openwork.timer enabled+active" "openwork.timer	enabled	active" "$(grep ^openwork $h/ev/pre/state.tsv)"
# P2 DRY switch/handoff/rollback compose (rc 0)
for s in switch handoff rollback; do t "DRY $s rc" 0 "$(DRY=1 cutover $h $s)"; done
t "DRY switch copies all 4 units" 4 "$(grep -c '+ cp .*/examples/systemd-unqualified/agent-loop' $h/ev/cutover.log)"
# N1 missing handler unit in the release -> capture/switch FAIL before any effect
h=$(mk n1); rm $h/rel/examples/systemd-unqualified/agent-loop-liveness-failed@.service
t "NEG missing handler: capture rc" 3 "$(cutover $h capture)"; t "NEG missing handler: reason" 1 "$(grep -c 'agent-loop-liveness-failed@.service missing' $h/ev/cutover.log)"
t "NEG missing handler: no systemctl effect (only read-only queries)" 0 "$(grep -c -E -- '--user (disable|enable|start|stop|restart|daemon-reload)' $h/systemctl.log 2>/dev/null || true)"
# N2 check unit without OnFailure -> FAIL
h=$(mk n2); sed -i '/^OnFailure=/d' $h/rel/examples/systemd-unqualified/agent-loop-liveness@.service
t "NEG no OnFailure wiring: capture rc" 3 "$(cutover $h capture)"
# N3 handler runs another command -> FAIL
h=$(mk n3); sed -i 's/checker-failed/liveness/' $h/rel/examples/systemd-unqualified/agent-loop-liveness-failed@.service
t "NEG wrong handler command: capture rc" 3 "$(cutover $h capture)"
# N4 a required command fails (disable of the old timers) -> switch FAILs, never PASS
h=$(mk n4); cutover $h capture >/dev/null; touch $h/fail-disable; sed -i 's/^QUALIFIED_SHA=.*/QUALIFIED_SHA='"$(sha256sum $h/rel/bin/agent-loop | cut -d' ' -f1)"'/' $h/inputs.env
r=$(cutover $h switch); t "NEG failed required command: switch rc" 3 "$r"; t "NEG failed required command: no switch PASS row" 0 "$(grep -c -P '^switch\tPASS' $h/ev/results.tsv 2>/dev/null || true)"
t "NEG failed required command: reason" 1 "$(grep -c 'required command failed: systemctl --user disable --now' $h/ev/cutover.log)"
# N5 rollback: handler drained before old owners; exactly the captured state restored; added unit files removed
h=$(mk n5); printf 'coax-dry.timer disabled\n' >/dev/null; sed -i '/^coax-dry.timer /d' $h/active; cutover $h capture >/dev/null
for u in agent-loop@.service agent-loop-liveness@.service agent-loop-liveness@.timer agent-loop-liveness-failed@.service; do cp $h/rel/examples/systemd-unqualified/$u $h/home/.config/systemd/user/; done
r=$(cutover $h rollback); t "rollback rc" 0 "$r"
L=$h/systemctl.log
fl=$(grep -n "is-active agent-loop-liveness-failed@campaign4.service" $L | head -1 | cut -d: -f1); el=$(grep -n "enable openwork.timer" $L | head -1 | cut -d: -f1)
t "rollback drains the handler before enabling old owners" yes "$( [ -n "$fl" ] && [ -n "$el" ] && [ "$fl" -lt "$el" ] && echo yes || echo "no($fl,$el)")"
t "rollback starts only captured-active timers (coax-dry was inactive)" 0 "$(grep -c 'start coax-dry.timer' $L)"
t "rollback re-enables captured-enabled coax-dry" 1 "$(grep -c 'enable coax-dry.timer' $L)"
t "rollback removes unit files the cutover added" 0 "$(ls $h/home/.config/systemd/user | wc -l)"
t "rollback does not recreate campaign4-watch (inactive at capture)" 0 "$(grep -c 'unit=campaign4-watch' $L)"
# N7 a seat id not registered under its role -> switch FAILs before any effect
h=$(mk n7); cutover $h capture >/dev/null; sed -i 's/^QUALIFIED_SHA=.*/QUALIFIED_SHA='"$(sha256sum $h/rel/bin/agent-loop | cut -d' ' -f1)"'/' $h/inputs.env; sed -i 's/^KILN_ID=.*/KILN_ID=00000000-bogus/' $h/inputs.env
t "NEG seat identity: switch rc" 3 "$(cutover $h switch)"; t "NEG seat identity: no disable ran" 0 "$(grep -c -- '--user disable' $h/systemctl.log || true)"
# N6 rollback without a captured state refuses (never guesses)
h=$(mk n6); t "NEG rollback without state.tsv: rc" 3 "$(cutover $h rollback)"
echo "TOTAL $n checks, $bad wrong"; cp -r $SB "$OUT/sandbox"; [ $bad -eq 0 ]
