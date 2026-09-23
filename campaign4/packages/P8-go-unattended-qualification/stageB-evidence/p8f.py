import json,os,subprocess,shutil,time,sqlite3
B="/home/bmosher/.local/bin/agent-loop"
def setup(name,wake_rc=0,ack=True):
    d="/tmp/p8f-"+name; shutil.rmtree(d,ignore_errors=True)
    for x in ("bin","stream","claims","art"): os.makedirs(d+"/"+x,exist_ok=True)
    calls=d+"/calls.log"; open(calls,"w").close()
    out='echo "wake: $1 -> started"' if ack else ':'
    stubs={"wake":"#!/usr/bin/env bash\necho \"wake $*\" >> %s\n%s\nexit %d\n"%(calls,out,wake_rc),
     "systemd-run":"#!/usr/bin/env bash\necho \"systemd-run $*\" >> %s\nexit 0\n"%calls,
     "systemctl":"#!/usr/bin/env bash\necho \"systemctl $*\" >> %s\nexit 0\n"%calls,
     "agent-deck":"#!/usr/bin/env bash\necho '[{\"id\":\"K\",\"title\":\"kiln\"},{\"id\":\"C\",\"title\":\"corvid\"},{\"id\":\"T\",\"title\":\"tern\"}]'\nexit 0\n"}
    for n,s in stubs.items(): open(d+"/bin/"+n,"w").write(s); os.chmod(d+"/bin/"+n,0o755)
    cfg={"project":"p8f","profile":"campaign4","wake":d+"/bin/wake","db":d+"/loop.db","stream_dir":d+"/stream","claims_dir":d+"/claims","artifacts_dir":d+"/art","director":"tern","seats":{"kiln":"K","corvid":"C","tern":"T"},"agent_deck":d+"/bin/agent-deck","bin":B,"systemd_run":d+"/bin/systemd-run","systemctl":d+"/bin/systemctl","max_verify_s":7200,"decision_window_s":86400}
    open(d+"/cfg.json","w").write(json.dumps(cfg))
    for sid in ("K","C"): open(d+"/stream/"+sid+".jsonl","w").write('{"t":"start","item":"i0"}\n{"t":"end","item":"i0"}\n')
    return d,calls
def run(d,*a):
    r=subprocess.run([B]+list(a),capture_output=True,text=True,cwd=d); return r.returncode,(r.stdout or "").strip(),(r.stderr or "").strip()
def wc(c): return sum(1 for l in open(c) if l.startswith("wake "))
def kv(d):
    con=sqlite3.connect("file:%s/loop.db?mode=ro"%d,uri=True); r=dict(con.execute("select key,value from driver_kv").fetchall()); con.close(); return r
print("== EVIDENCE/CLOSE: interrupted/absent verify claim ==")
d,c=setup("ev"); open(d+"/art/out.bin","w").write("hello")
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v")
run(d,"run","--config","cfg.json","--once")
run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin")
open(d+"/stream/K.jsonl","a").write('{"t":"start","item":"i1"}\n{"t":"end","item":"i1"}\n'); run(d,"run","--config","cfg.json","--once")
open(d+"/stream/C.jsonl","a").write('{"t":"start","item":"i2"}\n{"t":"end","item":"i2"}\n')
print("no verify claim:",run(d,"run","--config","cfg.json","--once")[1][:160])
print("again:",run(d,"run","--config","cfg.json","--once")[1][:160])
print("status closed?", "closed" in run(d,"status","--config","cfg.json")[1])
open(d+"/claims/ex-Q1-v1.json","w").write('{"package":"Q1","outcome":')  # interrupted/truncated
print("truncated claim:",run(d,"run","--config","cfg.json","--once")[1][:160])
print("status:\n"+run(d,"status","--config","cfg.json")[1])
print("== DEP negatives ==")
d,c=setup("dep")
print("unknown --after:",run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--after","NOPE")[:2])
print("self --after:",run(d,"dispatch","--config","cfg.json","--qid","QQ","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--after","QQ")[:2])
# non-permitting predecessor: close Q1 with blocked, Q2 --after Q1 must stay held
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v")
open(d+"/art/out.bin","w").write("hello"); run(d,"run","--config","cfg.json","--once")
run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin")
open(d+"/stream/K.jsonl","a").write('{"t":"start","item":"id1"}\n{"t":"end","item":"id1"}\n'); run(d,"run","--config","cfg.json","--once")
run(d,"claim","--config","cfg.json","--qid","Q1","--step","verify","--outcome","completed","--artifact","out.bin=out.bin")
open(d+"/stream/C.jsonl","a").write('{"t":"start","item":"id2"}\n{"t":"end","item":"id2"}\n'); run(d,"run","--config","cfg.json","--once")
run(d,"dispatch","--config","cfg.json","--qid","Q2","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--after","Q1")
w0=wc(c); run(d,"decide","--config","cfg.json","--qid","Q1","--kind","blocked","--ref","b1","--reason","no"); run(d,"run","--config","cfg.json","--once")
print("Q2 wakes after non-permitting predecessor:",wc(c)-w0)
print("status:\n"+run(d,"status","--config","cfg.json")[1])
print("== QUIET REST reopen ==")
w1=wc(c); run(d,"run","--config","cfg.json","--once"); run(d,"run","--config","cfg.json","--once")
print("new wakes after terminal:",wc(c)-w1)
print("== ACK receipt schema ==")
d,c=setup("ack2",wake_rc=1,ack=False)
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v")
run(d,"run","--config","cfg.json","--once")
k=kv(d); print("msg:",k.get("msg:msg-Q1-w1-1")); print("pending:",k.get("outbox-pending:ob-" , [x for x in k if 'outbox-pending' in x]))
