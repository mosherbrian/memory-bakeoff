# P12-live-measurement-1: pure evaluation functions for the live driver. No side effects: each reads its
# input (stdin or arguments) and prints "PASS|FAIL|INCOMPLETE detail" (or returns 0/1). Sourced by
# live-driver.sh and by evidence/live-measurement/checks-test.sh, which runs them on the saved live1 raws.
# Journal input is always read WHOLE by python (never `| grep -q`): under `set -o pipefail` an early-exit
# grep makes journalctl die of SIGPIPE and a real match reads as rc 141 (live1 L3a).

# l3a_eval ONSET_EPOCH RESTART_EPOCH < journal (-o short-unix): the watchdog killed THIS hang: a
# "Watchdog timeout" line and "Failed with result 'watchdog'" both at/after the onset and no later than
# the observed restart (+5 s). Lines before the onset are stale and ignored.
l3a_eval() { python3 -c '
import sys, re
onset, restart = float(sys.argv[1]), float(sys.argv[2]) + 5
wd = fr = stale = 0
for l in sys.stdin:
    m = re.match(r"^(\d+\.\d+) ", l)
    if not m: continue
    t = float(m.group(1)); inwin = onset <= t <= restart
    if "Watchdog timeout" in l: wd += inwin; stale += not inwin
    if "Failed with result '"'"'watchdog'"'"'" in l: fr += inwin
if wd and fr: print("PASS watchdog timeout and result watchdog inside the onset..restart window")
elif stale and not wd: print("FAIL only a watchdog line outside the onset..restart window (stale or unrelated)")
else: print("FAIL no watchdog timeout (%d) / result watchdog (%d) inside the window" % (wd, fr))
' "$1" "$2"; }

# start_limit_eval ONSET_EPOCH UNIT BURST < journal (-o short-unix): a real restart loop of THIS unit after the
# onset (ruling restart-classification-ruling.json): at least BURST-1 "Scheduled restart job" lines, each after a
# failed start, and then systemd's rate-limit refusal "Start request repeated too quickly", all for UNIT and at/after
# the onset. systemd (258 here) then keeps Result=exit-code, so Result alone is not evidence. A single crash, a
# stale (pre-onset) line or another unit's line is not a restart loop.
start_limit_eval() { python3 -c '
import sys, re
onset, unit, burst = float(sys.argv[1]), sys.argv[2], int(sys.argv[3]); hit = restarts = fails = 0
for l in sys.stdin:
    m = re.match(r"^(\d+\.\d+) ", l)
    if not m or float(m.group(1)) < onset or (unit + ":") not in l: continue
    hit += "Start request repeated too quickly" in l; restarts += "Scheduled restart job" in l
    fails += "Failed with result" in l
if hit and restarts >= burst - 1 and fails >= burst - 1: print("PASS restart loop of %s: %d scheduled restarts, %d failed starts, then the start limit" % (unit, restarts, fails))
else: print("FAIL no proven restart loop of %s after the onset (restarts %d, failed starts %d, start-limit line %d; burst %d)" % (unit, restarts, fails, hit, burst))
' "$1" "$2" "$3"; }

# stop_exit_eval < journal (-o cat, since the stop onset): run itself logged its intentional exit 64.
stop_exit_eval() { python3 -c '
import sys
print("PASS run logged its exit 64" if any("stop requested; exiting 64" in l for l in sys.stdin) else "FAIL no exit-64 line since the stop onset")'; }

# healthy_eval EPOCH "STATE CHECKED_AT INCIDENT": ok or rest, checked at/after EPOCH (not a verdict from
# before the event). rest is the healthy idle state (no open work); unknown/crashed/hung/starting never are.
healthy_eval() { python3 -c '
import sys, datetime as D
ep = float(sys.argv[1]); f = (sys.argv[2] + "  ").split(" ")
try: c = D.datetime.strptime(f[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=D.timezone.utc).timestamp()
except Exception: sys.exit(1)
sys.exit(0 if f[0] in ("ok", "rest") and c >= ep else 1)' "$1" "$2"; }

# l6_argv_eval EXPECTED_BIN CONFIG QID < ExecStart value: the transient deadline unit's exact callback argv,
# captured while the unit exists. It must be EXACTLY: BIN timer-callback --config CONFIG --qid QID
# --action QID-w1 --execution ex-QID-w1 (no extra, duplicate, missing or reordered argument). Prints the argv
# (one line) or "INCOMPLETE why" and returns 1.
l6_argv_eval() { python3 -c '
import sys, re
b, cfg, q = sys.argv[1:4]; s = sys.stdin.read()
m = re.findall(r"argv\[\]=([^;]*);", s)
a = m[0].split() if len(m) == 1 else []
want = [b, "timer-callback", "--config", cfg, "--qid", q, "--action", q + "-w1", "--execution", "ex-" + q + "-w1"]
ok = a == want
print(" ".join(a) if ok else "INCOMPLETE callback argv is not exactly %s: got %r" % (" ".join(want), " ".join(a) if a else s[:200])); sys.exit(0 if ok else 1)' "$1" "$2" "$3"; }

# pass_eval EPOCH INVOCATION MAINPID < loop-pass JSON (the ledger's authoritative pass record, read-only):
# a pass completed at/after EPOCH by the CURRENT run (same systemd invocation and main pid). A fresh checker
# timestamp or a check count is not pass evidence. Missing, malformed, stale or another incarnation: fail.
pass_eval() { python3 -c '
import sys, json, datetime as D
ep, inv, pid = float(sys.argv[1]), sys.argv[2], sys.argv[3]
try:
    p = json.loads(sys.stdin.read()); at = D.datetime.strptime(p["at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=D.timezone.utc).timestamp()
except Exception: sys.exit(1)
sys.exit(0 if at >= ep and inv and p.get("invocation") == inv and str(p.get("pid")) == pid else 1)' "$1" "$2" "$3"; }

# l6_replay_eval RC WORKER_BEFORE WORKER_AFTER DIRECTOR_BEFORE DIRECTOR_AFTER < replay output: the replayed
# callback ran (rc 0), the core said already-handled, and no new /cancel or director wake happened.
l6_replay_eval() { python3 -c '
import sys, json
rc, w0, w1, d0, d1 = (int(x) for x in sys.argv[1:6]); out = sys.stdin.read()
dec = [json.loads(l).get("decision") for l in out.splitlines() if l.startswith("{\"decision\"")]
if rc != 0: print("FAIL replay rc %d: %s" % (rc, out.strip()[:160]))
elif "already-handled" not in dec: print("FAIL replay decision %s (want already-handled)" % dec)
elif w1 != w0 or d1 != d0: print("FAIL replay repeated effects: worker %d->%d director %d->%d" % (w0, w1, d0, d1))
else: print("PASS replay ran (rc 0): already-handled, no new /cancel or director wake")' "$@"; }
