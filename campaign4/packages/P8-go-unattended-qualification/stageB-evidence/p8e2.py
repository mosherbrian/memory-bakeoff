import json,os,subprocess,shutil,time,sqlite3
B="/home/bmosher/.local/bin/agent-loop"
def setup(name,wake_rc=0):
    d="/tmp/p8e2-"+name; shutil.rmtree(d,ignore_errors=True)
    for x in ("bin","stream","claims","art"): os.makedirs(d+"/"+x,exist_ok=True)
    calls=d+"/calls.log"; open(calls,"w").close()
    wake="#!/usr/bin/env bash\necho \"wake $*\" >> %s\nif [ \"$2\" = \"/cancel\" ]; then echo \"wake: $1 -> cancel-acked\"; else echo \"wake: $1 -> started\"; fi\nexit %d\n"%(calls,wake_rc)
    stubs={"wake":wake,
     "systemd-run":"#!/usr/bin/env bash\necho \"systemd-run $*\" >> %s\nexit 0\n"%calls,
     "systemctl":"#!/usr/bin/env bash\necho \"systemctl $*\" >> %s\nexit 0\n"%calls,
     "agent-deck":"#!/usr/bin/env bash\necho '[{\"id\":\"K\",\"title\":\"kiln\"},{\"id\":\"C\",\"title\":\"corvid\"},{\"id\":\"T\",\"title\":\"tern\"}]'\nexit 0\n"}
    for n,s in stubs.items(): open(d+"/bin/"+n,"w").write(s); os.chmod(d+"/bin/"+n,0o755)
    cfg={"project":"p8e2","profile":"campaign4","wake":d+"/bin/wake","db":d+"/loop.db","stream_dir":d+"/stream","claims_dir":d+"/claims","artifacts_dir":d+"/art","director":"tern","seats":{"kiln":"K","corvid":"C","tern":"T"},"agent_deck":d+"/bin/agent-deck","bin":B,"systemd_run":d+"/bin/systemd-run","systemctl":d+"/bin/systemctl","max_verify_s":7200,"decision_window_s":86400}
    open(d+"/cfg.json","w").write(json.dumps(cfg))
    for sid in ("K","C"): open(d+"/stream/"+sid+".jsonl","w").write('{"t":"start","item":"i0"}\n{"t":"end","item":"i0"}\n')
    return d,calls
def run(d,*a):
    r=subprocess.run([B]+list(a),capture_output=True,text=True,cwd=d); return r.returncode,(r.stdout or "").strip(),(r.stderr or "").strip()
def wc(c): return sum(1 for l in open(c) if l.startswith("wake "))
print("== DUE (duration=1s) ==")
d,c=setup("due")
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--duration","1s")
run(d,"run","--config","cfg.json","--once"); time.sleep(2.2)
for i in (1,2,3):
    rc,o,e=run(d,"timer-callback","--config","cfg.json","--qid","Q1","--action","Q1-w1","--execution","ex-Q1-w1")
    print("callback",i,"rc",rc,"out",o[:140],"err",e[:120])
print("wake calls:",wc(c)); print(open(c).read())
print("status:\n"+run(d,"status","--config","cfg.json")[1])
print("== ACK refused (wake rc=1) ==")
d,c=setup("ack",wake_rc=1)
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v")
print("run1",run(d,"run","--config","cfg.json","--once")[1][:120],"wakes",wc(c))
print("run2",run(d,"run","--config","cfg.json","--once")[1][:120],"wakes",wc(c))
print("run3",run(d,"run","--config","cfg.json","--once")[1][:120],"wakes",wc(c))
