import json, os, sys
sys.path.insert(0, "/tmp/p6r11-cand-repro")
import test_cand as T

def show(env, case, tag):
    rec = T.receipt(env, case)
    print("=== %s receipt ===" % tag)
    print(json.dumps(rec, indent=1, sort_keys=True)[:4000])

# FV-W on candidate
env = T.make_suite(T.R9)
try:
    T.arm(env, "failed-verification", "corrupt-after-worker")
    r = T.run_case(env, "failed-verification", {env["wt"]: 18.0})
    print("FV-W rc=", r.returncode)
    print("FV-W stdout=", r.stdout.strip()[:1500])
    print("FV-W stderr=", r.stderr.strip()[:1500])
    show(env, "failed-verification", "FV-W")
finally:
    T.close(env)

# QR-W on candidate
env = T.make_suite(T.R9)
try:
    T.arm(env, "quiet-rest", "none-declared")
    r = T.run_case(env, "quiet-rest", {env["wt"]: 18.0})
    print("QR-W rc=", r.returncode)
    print("QR-W stdout=", r.stdout.strip()[:1500])
    show(env, "quiet-rest", "QR-W")
finally:
    T.close(env)
