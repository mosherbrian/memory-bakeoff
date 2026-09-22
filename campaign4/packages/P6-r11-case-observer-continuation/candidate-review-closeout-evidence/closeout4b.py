import json, os, sys, hashlib
sys.path.insert(0,"/tmp/p6r11-rej-repro")
import test_cand as T
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
env=T.make_suite(T.R9)
try:
    b=json.load(open(env["binding"]))
    b["worker"]["incarnation"]["ino"]=999999
    json.dump(b,open(env["binding"],"w"))
    # derive sig binds mutated binding
    dsig=os.path.join(env["tmp"],"dsig.json")
    json.dump({"signer":"tern","purpose":"derive-only","plan_sha256":sha(env["plan"]),
               "binding_sha256":sha(env["binding"])},open(dsig,"w"))
    cfg=os.path.join(env["tmp"],"execution-config2.json")
    r=T.cli(T.R9SCRIPT,T.R9,"derive-config","--plan",env["plan"],"--binding",env["binding"],"--signatures",dsig,"--out",cfg)
    print("re-derive rc",r.returncode, r.stdout.strip()[:120], r.stderr.strip()[:120])
    if r.returncode==0:
        sig=os.path.join(env["tmp"],"sig2.json")
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
        print("wrong-incarnation run rc",r.returncode,"stdout",r.stdout.strip()[:250],"stderr",r.stderr.strip()[:120])
finally:
    T.close(env)
