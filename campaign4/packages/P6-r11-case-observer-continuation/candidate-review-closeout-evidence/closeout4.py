import json, os, sys, hashlib, subprocess
sys.path.insert(0,"/tmp/p6r11-rej-repro")
import test_cand as T
H="/home/bmosher/memory-bake-off/campaign4/packages/P6-r11-case-observer-continuation/candidate/src/r3harness/harness.py"
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()

# check 3b: proper reattach (global opts before subcommand)
env=T.make_suite(T.R9)
try:
    T.arm(env,"failed-verification","corrupt-after-worker")
    r=T.run_case(env,"failed-verification",{"alpha-12":18.0})
    print("first rc",r.returncode, r.stdout.strip()[:120])
    croot=os.path.join(env["tmp"],"failed-verification"); cplan=os.path.join(croot,"candidate-plan.json")
    rr=T.cli(H,T.R9,"--live","--plan",cplan,"--plan-hash",sha(cplan),
             "--allowlist-seat",env["wt"],"--allowlist-seat",env["vt"],
             "--db",os.path.join(croot,"fixture.db"),"--manifest",os.path.join(croot,"manifest.json"),
             "--claims",os.path.join(croot,"claims"),"--qid","P6C","reattach")
    print("reattach(proper) rc",rr.returncode,"stdout",rr.stdout.strip()[:200],"stderr",rr.stderr.strip()[:150])
    import sqlite3
    con=sqlite3.connect("file:%s?mode=ro"%os.path.join(croot,"fixture.db"),uri=True)
    kv=dict(con.execute("select key,value from driver_kv").fetchall())
    print("msg-counter",kv.get("msg-counter"),"rej",[k for k in kv if k.startswith("verified-rejection")])
finally:
    T.close(env)

# check 4: wrong incarnation -> gate E_REBOUND at run-case CLI
env=T.make_suite(T.R9)
try:
    b=json.load(open(env["binding"]))
    b["worker"]["incarnation"]["ino"]=999999
    json.dump(b,open(env["binding"],"w"))
    cfg=os.path.join(env["tmp"],"execution-config2.json")
    sig=os.path.join(env["tmp"],"sig2.json")
    r=T.cli(T.R9SCRIPT,T.R9,"derive-config","--plan",env["plan"],"--binding",env["binding"],"--signatures",env["sig"],"--out",cfg)
    print("re-derive rc",r.returncode)
    json.dump({"signer":"tern","purpose":"stagec-task","plan_sha256":sha(env["plan"]),
               "binding_sha256":sha(env["binding"]),"config_sha256":sha(cfg),
               "stagec_entry_sha256":sha(T.R9SCRIPT),
               "candidate_harness_sha256":"cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142",
               "r3_harness_sha256":sha(os.path.join(T.R9SRC,"r3harness","harness.py")),
               "fixture_control_sha256":sha(os.path.join(T.R9SRC,"fixture_control.py")),
               "deposit_sha256":sha(T.R9DEPOSIT),"seat_emulator_sha256":sha(T.R9SEAT),
               "fault_onset_sha256":sha(os.path.join(T.R9SRC,"fault_onset.py"))},open(sig,"w"))
    r=T.cli(T.R9SCRIPT,T.R9,"run-case","--config",cfg,"--plan",env["plan"],"--signatures",sig,
            "--case","failed-verification","--suite-root",env["tmp"],"--registry-file",env["reg"],
            "--out",os.path.join(env["tmp"],"fv2","receipt.json"))
    print("wrong-incarnation run rc",r.returncode,"stdout",r.stdout.strip()[:250],"stderr",r.stderr.strip()[:150])
finally:
    T.close(env)
