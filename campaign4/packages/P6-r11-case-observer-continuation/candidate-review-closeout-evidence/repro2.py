import json, os, sys, subprocess, hashlib
sys.path.insert(0, "/tmp/p6r11-rej-repro")
import test_cand as T

R3 = "/home/bmosher/memory-bake-off/campaign4/packages/P6-r11-case-observer-continuation/candidate/src/r3harness/harness.py"
CAND = "/home/bmosher/memory-bake-off/campaign4/packages/P6-r11-case-observer-continuation/candidate"

def show(tag, r, rec):
    print("== %s rc=%s" % (tag, r.returncode))
    print("   stdout:", r.stdout.strip()[:300])
    for k in ("sends", "timecheck", "outcome", "committed_actions"):
        if k in rec:
            print("   %s = %s" % (k, json.dumps(rec[k])[:200]))

def run(tag, case, control, delays=None, bounds=None, live_stop_in=None):
    env = T.make_suite(T.R9, bounds=bounds, live_stop_in=live_stop_in)
    try:
        T.arm(env, case, control)
        r = T.run_case(env, case, delays or {})
        show(tag, r, T.receipt(env, case))
        return env, r
    finally:
        T.close(env)

# check 2
run("QR-WV", "quiet-rest", "none-declared", {"alpha-12": 18.0, "omega-07": 18.0})
run("FV-EXPIRY", "failed-verification", "corrupt-after-worker", {"alpha-12": 40.0},
    bounds={"duration_s": 15, "escalation_window_s": 30})
run("QR-EXPIRY", "quiet-rest", "none-declared", {"alpha-12": 40.0},
    bounds={"duration_s": 15, "escalation_window_s": 30})
run("FV-OUTER-STOP", "failed-verification", "corrupt-after-worker", {"alpha-12": 25.0},
    live_stop_in=12)

# check 3: replay/reopen at production CLI boundary
env = T.make_suite(T.R9)
try:
    T.arm(env, "failed-verification", "corrupt-after-worker")
    r = T.run_case(env, "failed-verification", {"alpha-12": 18.0})
    show("FV-W-first", r, T.receipt(env, "failed-verification"))
    croot = os.path.join(env["tmp"], "failed-verification")
    cplan = os.path.join(croot, "candidate-plan.json")
    def sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    # reopen via production reattach CLI, same action/execution
    rr = T.cli(R3, T.R9, "reattach", "--live", "--plan", cplan,
               "--plan-hash", sha(cplan), "--allowlist-seat", env["wt"],
               "--allowlist-seat", env["vt"], "--db",
               os.path.join(croot, "fixture.db"), "--manifest",
               os.path.join(croot, "manifest.json"), "--claims",
               os.path.join(croot, "claims"), "--qid", "P6C")
    print("== FV-W-reopen rc=%s" % rr.returncode)
    print("   stdout:", rr.stdout.strip()[:300])
    # durable rejection + no new sends
    import sqlite3
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(croot, "fixture.db"), uri=True)
    kv = dict(con.execute("select key,value from driver_kv").fetchall())
    rej = [k for k in kv if k.startswith("verified-rejection:")]
    print("   msg-counter:", kv.get("msg-counter"), "verified-rejection keys:", rej)
    if rej:
        print("   rejection record:", kv[rej[0]][:200])
finally:
    T.close(env)
