#!/bin/bash
# P13 promotion plan v2 sandbox proof. Everything under a private root: files, unit states (stateful systemctl
# double), ledger DB. Production paths are only READ to copy the old binary/config bytes. Every row SANDBOX-*.
set -u
P=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
n=0; bad=0; ok() { n=$((n+1)); echo "ok   $1"; }; no() { n=$((n+1)); bad=$((bad+1)); echo "FAIL $1"; }
setup() { # SCENARIO -> fresh sandbox in $T
  T=$(mktemp -d /tmp/p13promo-XXXX); R=$T/root; H=$R/home/bmosher
  mkdir -p $H/.local/bin $H/.config/agent-loop $H/.config/agent-deck $T/db $T/sbin
  cp /home/bmosher/.local/bin/agent-loop $H/.local/bin/agent-loop
  python3 -c "import json,sys; c=json.load(open('/home/bmosher/.config/agent-loop/campaign4.json')); c['db']='$T/db/campaign4.db'; c['wake']='/bin/true'; c['agent_deck']='/bin/true'; json.dump(c,open('$H/.config/agent-loop/campaign4.json','w'),indent=1)"
  python3 -c "import json,sys; c=json.load(open('$P/plans/campaign4-decision-config.prospective.json')); c['db']='$T/db/campaign4.db'; c['wake']='/bin/true'; c['agent_deck']='/bin/true'; json.dump(c,open('$T/prospective.json','w'),indent=1)"
  cp -p /home/bmosher/.config/agent-deck/escalation-watch $H/.config/agent-deck/escalation-watch   # resolver ABSENT, as on the host
  printf 'agent-loop-liveness@campaign4.timer\tactive\tenabled\nescalation-watch.timer\tactive\tenabled\nagent-loop@campaign4.service\tactive\tenabled\nagent-loop-liveness@campaign4.service\tinactive\tstatic\nagent-loop-liveness-failed@campaign4.service\tinactive\tstatic\nescalation-watch.service\tinactive\tstatic\n' > $T/units.tsv
  echo old-inv > $T/inv
  cat > $T/sbin/systemctl <<SC
#!/bin/bash
# stateful systemctl double (sandbox); on start of the loop: new invocation, and a loop-pass record per STUB_PASS
S=$T/units.tsv; a=(\$@); [ "\${a[0]}" = --user ] && a=("\${a[@]:1}")
case "\${a[0]}" in
 is-active) awk -F'\t' -v u="\${a[1]}" '\$1==u{print \$2}' \$S;;
 is-enabled) awk -F'\t' -v u="\${a[1]}" '\$1==u{print \$3}' \$S;;
 stop|start) st=inactive; [ "\${a[0]}" = start ] && st=active
   [ "\${a[0]}" = start ] && [ -n "\${STUB_FAIL_START:-}" ] && [ "\${a[1]}" = "\$STUB_FAIL_START" ] && exit 1
   awk -F'\t' -v OFS='\t' -v u="\${a[1]}" -v s=\$st '\$1==u{\$2=s}1' \$S > \$S.n && mv \$S.n \$S
   if [ "\${a[0]}" = start ] && [ "\${a[1]}" = agent-loop@campaign4.service ]; then
     inv=\$(head -c8 /dev/urandom | od -An -tx1 | tr -d ' \n'); old=\$(cat $T/inv); echo \$inv > $T/inv; echo \$\$ > $T/pid
     pinv=\$inv; [ "\${STUB_PASS:-fresh}" = stale ] && pinv=\$old
     python3 -c "import sqlite3,json,time,sys; c=sqlite3.connect('$T/db/campaign4.db'); c.execute('create table if not exists driver_kv(key text primary key, value text)'); c.execute('insert or replace into driver_kv values(?,?)',('loop-pass',json.dumps({'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'invocation':sys.argv[1],'pid':int(sys.argv[2])}))); c.commit()" \$pinv \$\$
   fi;;
 show) for x in "\${a[@]}"; do :; done; case "\$*" in *InvocationID*) cat $T/inv;; *MainPID*) cat $T/pid 2>/dev/null || echo 0;; esac;;
 daemon-reload) ;;
 *) exit 1;;
esac
SC
  chmod 755 $T/sbin/systemctl
  { echo RUN=sbx; grep -E '^ADAPTER_(WATCH|RESOLVE)_(SRC|SHA)=' "$P/plans/live-p13-inputs.template.env"; } > $T/in.env
  snapshot_files() { for f in $H/.local/bin/agent-loop $H/.config/agent-loop/campaign4.json $H/.config/agent-deck/escalation-watch $H/.config/agent-deck/escalation-resolve; do [ -e $f ] && echo "$f $(sha256sum < $f | cut -c1-16) $(stat -c %a $f)" || echo "$f ABSENT"; done; cut -f1,2 $T/units.tsv; }
}
go() { PROMOTE_SANDBOX=1 PROMOTE_ROOT=$R PROMOTE_SYSTEMCTL=$T/sbin/systemctl PROMOTE_PROSPECTIVE=$T/prospective.json PROMOTE_EV=$T/ev bash "$P/plans/promotion-plan.sh" $T/in.env "${1:-run}" > $T/out 2>&1; }
# 1 stale pass -> PROMOTE FAIL, exact restore incl. absent resolver removed
setup; B=$(snapshot_files); STUB_PASS=stale go; rc=$?
[ $rc = 3 ] && grep -q "no fresh ledger pass" $T/out && ok "stale pass (old invocation) rejected -> PROMOTE FAIL rc 3" || no "stale pass rc $rc: $(tail -2 $T/out)"
grep -q "ROLLBACK	SANDBOX-PASS" $T/ev/promotion-results.tsv && [ "$B" = "$(snapshot_files)" ] && ok "exact restore: files/modes/units equal the snapshot" || no "restore not exact"
[ ! -e $H/.config/agent-deck/escalation-resolve ] && ok "absent resolver restored as ABSENT (introduced file removed, none fabricated)" || no "resolver left behind"
cp -r $T/ev $P/evidence/promotion-closure/sbx-stale-pass; rm -rf $T
# 2 partial install failure (adapter dir not writable after the binary install) -> restore
setup; B=$(snapshot_files); chmod 555 $H/.config/agent-deck; go; rc=$?; chmod 755 $H/.config/agent-deck
[ $rc = 3 ] && grep -q "watch adapter install" $T/out && ok "partial install failure -> PROMOTE FAIL rc 3" || no "partial install rc $rc: $(tail -2 $T/out)"
[ "$B" = "$(snapshot_files)" ] && grep -q "ROLLBACK	SANDBOX-PASS" $T/ev/promotion-results.tsv && ok "partial install: binary and units restored exactly" || no "partial install restore not exact"
cp -r $T/ev $P/evidence/promotion-closure/sbx-partial-install; rm -rf $T
# 3 start failure of the loop -> restore; unit states back
setup; B=$(snapshot_files); STUB_FAIL_START=agent-loop@campaign4.service go; rc=$?
[ $rc = 3 ] && grep -q "start agent-loop@campaign4.service" $T/out && grep -q "ROLLBACK	SANDBOX-FAIL" $T/ev/promotion-results.tsv && ok "start failure -> PROMOTE FAIL; restore cannot restart the still-failing loop and says ROLLBACK FAIL (not a false PASS)" || no "start failure rc $rc"
rm -rf $T
# 4 rollback failure is nonzero: remove the archive copy of the binary, then rollback mode
setup; STUB_PASS=stale go; rm -f $T/ev/promo-archive/f1; echo junk > $H/.local/bin/agent-loop; go rollback; rc=$?
[ $rc != 0 ] && grep -q "ROLLBACK	SANDBOX-FAIL" $T/ev/promotion-results.tsv && ok "a failed rollback exits nonzero (rc $rc) and records ROLLBACK FAIL" || no "failed rollback rc $rc"
rm -rf $T
# 5 guard failure mutates nothing
setup; B=$(snapshot_files); cp $T/prospective.json $T/p.bak; python3 -c "import json; c=json.load(open('$T/prospective.json')); c['decision_ladder']=c['decision_ladder'][:2]; json.dump(c,open('$T/prospective.json','w'))"; go; rc=$?
[ $rc = 3 ] && grep -q "prospective config refused" $T/out && [ "$B" = "$(snapshot_files)" ] && [ ! -d $T/ev/promo-archive ] && ok "invalid policy refused by the guard; nothing changed, no snapshot taken" || no "guard rc $rc"
rm -rf $T
echo "promotion-sandbox: $n checks, $bad wrong"; [ $bad -eq 0 ]
