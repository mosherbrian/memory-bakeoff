import json, sys
sys.path.insert(0, "/tmp/p6r11-rej-repro")
import test_cand as T
import datetime
def run(case, delays, control):
    env = T.make_suite(T.R9)
    try:
        T.arm(env, case, control)
        r = T.run_case(env, case, delays)
        rec = T.receipt(env, case)
        print("== %s rc=%s" % (case, r.returncode))
        print("stdout:", r.stdout.strip()[:400])
        for k in ("sends","outcome","committed_actions","timecheck","verified_rejection","worker_item","verifier_item"):
            if k in rec: print("  %s = %s" % (k, json.dumps(rec[k])[:400]))
        return rec
    finally:
        T.close(env)
run("failed-verification", {"alpha-12":18.0}, "corrupt-after-worker")
run("failed-verification", {"alpha-12":18.0, "omega-07":18.0}, "corrupt-after-worker")
run("quiet-rest", {"alpha-12":18.0}, "none-declared")
