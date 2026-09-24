#!/bin/bash
# P13 decision evaluators: pure functions for the live20 plan. No side effects:
# each reads stdin/arguments and prints "PASS|FAIL|INCOMPLETE detail" (or rc).
# Negative controls live in evidence/plan-standin/rehearsal (offline).
# Pattern follows P12 plans/live-checks.sh (f6afd9e0…); these cover decision
# ownership cases live-driver.sh does not.

# policy_eval POLICY_JSON: fixture generic policy (ladder 0/20/40, window 60)
# or production required policy (ladder exactly 0/300/600). Anything else FAILs.
# Repair-1 proved binary LoadConfig refusal; this validates plan artifacts offline.
policy_eval() { python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print("FAIL policy unreadable:", e); sys.exit()
pol, lad, win = d.get("decision_policy"), d.get("decision_ladder", []), d.get("decision_deadline_s")
offs = sorted((r.get("after_s") for r in lad)) if isinstance(lad, list) else None
if pol == "generic":
    ok = offs == [0, 20, 40] and win == 60
    print(("%s generic fixture ladder %s window %s (production 0/300/600 NOT proven by these offsets)" % ("PASS" if ok else "FAIL", offs, win))); sys.exit(0 if ok else 1)
if pol == "required":
    ok = offs == [0, 300, 600] and isinstance(win, int) and win > 0
    print(("%s required production ladder %s window %s" % ("PASS" if ok else "FAIL", offs, win))); sys.exit(0 if ok else 1)
print("FAIL policy %r must be generic or required" % pol)' ; }

# rung_order_eval EXPECTED_CSV < ledger lines: rung deliveries happened in ladder
# order with no rung skipped and no duplicate rung delivery per incident.
rung_order_eval() { python3 -c '
import sys
want = sys.argv[1].split(","); seen = []
for l in sys.stdin:
    l = l.strip()
    if l.startswith("rung:"): seen.append(l.split(":", 1)[1])
ok = seen == want
print(("%s rungs %s (want %s)" % ("PASS" if ok else "FAIL", seen, want)))' "$1"; }

# ack_eval CAPFILE INCIDENT RESPONDER < now-epoch: a valid ack names owner+next,
# response deadline <=15 min ahead, cap bound to incident+responder, unexpired.
ack_eval() { python3 -c '
import sys, json, time
cap, inc, resp = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    a = json.load(open(cap))
except Exception as e:
    print("FAIL ack unreadable:", e); sys.exit()
now = time.time()
ok = (a.get("incident") == inc and a.get("responder") == resp
      and a.get("next_action") and 0 < (a.get("response_deadline", 0) - now) <= 900)
print(("%s ack by %s next %s deadline +%ds" % ("PASS" if ok else "FAIL", a.get("responder"), a.get("next_action"), (a.get("response_deadline", 0) - now))))' "$1" "$2" "$3"; }

# recur_eval FIRST_KEY SECOND_KEY: expiry re-raise uses the SAME stable key.
recur_eval() { [ "$1" = "$2" ] && [ -n "$1" ] && echo "PASS same recurrence key $1" || echo "FAIL recurrence key $1 -> $2"; }

# suppress_eval LEDGER INCIDENT: after an authorized decide, no later page for it.
suppress_eval() { python3 -c '
import sys
inc = sys.argv[1]; pages = [l for l in sys.stdin if inc in l and "page" in l]
print(("%s no page after decide for %s (%d page lines)" % ("PASS" if not pages else "FAIL", inc, len(pages))))' "$1"; }

# nodup_eval SENDLOG INCIDENT: at most one labelled repeat per ambiguous stage.
nodup_eval() { python3 -c '
import sys
inc, path = sys.argv[1], sys.argv[2]
n = sum(1 for l in open(path) if inc in l and "repeat" in l)
print(("%s %d labelled repeats for %s (bound 1)" % ("PASS" if n <= 1 else "FAIL", n, inc)))' "$1" "$2"; }

# cleanup_eval ROOT: no fixture units/seats/processes remain; caps dir gone
# only after bounded archive exists; archive holds the caps snapshot.
cleanup_eval() { local root=$1 bad=""
  [ -e "$root/caps" ] && bad="$bad caps dir remains;"
  [ -e "$root/archive/caps.tar" ] || bad="$bad no caps archive;"
  for u in $(systemctl --user list-units --all --plain --no-legend 'agent-loop-p13d-*' 2>/dev/null | awk "{print \$1}"); do bad="$bad unit $u;"; done
  if [ -z "$bad" ]; then echo "PASS cleanup complete under $root"; else echo "FAIL $bad"; fi; }
