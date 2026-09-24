# P13 rung evaluator (pure; sourced by live-p13-driver.sh, unit-tested by evidence/live-composition/rung-eval-test.sh).
# rung_eval DBSTATE LOG SID INCIDENT DEADLINE_EPOCH -> rc 0 only if the product DB records the rung "sent ..."
# AND the wake send log has a row to exactly SID, state started OR queued (wake rc 0 or 3: both are real
# receipts), at/after the deadline, whose text names "DECISION OVERDUE <incident>". Unrelated wakes (other
# text, other seat, before the deadline, failed state) and a null/absent DB rung never count.
rung_eval() { case "$1" in sent*) ;; *) return 1;; esac
  python3 - "$2" "$3" "$4" "$5" <<'PY'
import sys, datetime as D
log, sid, inc, dl = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]); ok = False
for l in open(log, errors="replace"):
    f = l.rstrip("\n").split("\t")
    if len(f) < 8 or f[3] != sid or not (f[4] == "started" or f[4].startswith("queued")): continue
    if ("DECISION OVERDUE " + inc) not in f[7]: continue
    try: t = D.datetime.strptime(f[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=D.timezone.utc).timestamp()
    except Exception: continue
    ok = ok or t >= dl
sys.exit(0 if ok else 1)
PY
}
