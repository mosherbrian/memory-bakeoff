import os,sys,json
sys.path.insert(0,"/home/bmosher/memory-bake-off/campaign4/packages/P6-r9-observer-lifetime/tests")
import test_observer_lifetime as T
env=T.make_suite(T.R9SCRIPT,T.R9SEAT,T.R9DEPOSIT,T.R9PLAN,T.R9)
try:
    T.arm(env,"positive-handoff")
    r=T.run_case(env,"positive-handoff",{env["wt"]:18.0})
    print("rc",r.returncode,r.stdout.strip()[:150])
    lp=os.path.join(env["tmp"],"positive-handoff","latency.jsonl")
    rows=[json.loads(l) for l in open(lp) if l.strip()]
    print("latency rows",len(rows))
    for x in rows: print("  ",x.get("action"),x.get("outcome"),x.get("detection_latency_s"),x.get("worker_duration_s"))
    outs=[x.get("outcome") for x in rows]
    print("[4] REPRODUCED" if ("no-end-failure" in outs and any(o in ("transition-committed","terminal-rest") for o in outs)) else "[4] NOT REPRODUCED")
finally:
    T.close(env)
