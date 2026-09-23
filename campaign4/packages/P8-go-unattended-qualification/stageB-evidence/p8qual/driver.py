import json,os,subprocess,shutil,hashlib,sys
B="/home/bmosher/.local/bin/agent-loop"
ROOT="/tmp/p8qual"
STUBS={
 "wake": "#!/usr/bin/env bash\necho \"wake $*\" >> CALLS\necho \"wake: $1 -> started\"\nexit 0\n",
 "systemd-run": "#!/usr/bin/env bash\necho \"systemd-run $*\" >> CALLS\nexit 0\n",
 "systemctl": "#!/usr/bin/env bash\necho \"systemctl $*\" >> CALLS\necho active\nexit 0\n",
 "agent-deck": "#!/usr/bin/env bash\necho '[{\"id\":\"K\",\"title\":\"kiln\"},{\"id\":\"C\",\"title\":\"corvid\"},{\"id\":\"T\",\"title\":\"tern\"}]'\nexit 0\n",
}
def setup(name,seats=None):
    d=os.path.join(ROOT,name); shutil.rmtree(d,ignore_errors=True)
    for x in ("bin","stream","claims","art"): os.makedirs(os.path.join(d,x),exist_ok=True)
    calls=os.path.join(d,"calls.log"); open(calls,"w").close()
    for n,s in STUBS.items():
        p=os.path.join(d,"bin",n); open(p,"w").write(s.replace("CALLS",calls)); os.chmod(p,0o755)
    seats=seats or {"kiln":"K","corvid":"C","tern":"T"}
    cfg={"project":"p8qual","profile":"campaign4","wake":d+"/bin/wake","db":d+"/loop.db","stream_dir":d+"/stream","claims_dir":d+"/claims","artifacts_dir":d+"/art","director":"tern","seats":seats,"agent_deck":d+"/bin/agent-deck","bin":B,"systemd_run":d+"/bin/systemd-run","systemctl":d+"/bin/systemctl","max_verify_s":7200,"decision_window_s":86400}
    open(os.path.join(d,"cfg.json"),"w").write(json.dumps(cfg))
    for sid in set(seats.values()):
        open(os.path.join(d,"stream",sid+".jsonl"),"w").write('{"t":"start","item":"i0"}\n{"t":"end","item":"i0"}\n')
    return d,calls
def run(d,*args):
    r=subprocess.run([B]+list(args),capture_output=True,text=True,cwd=d)
    return r.returncode,(r.stdout or "").strip(),(r.stderr or "").strip()
def endturn(d,sid,item):
    open(os.path.join(d,"stream",sid+".jsonl"),"a").write('{"t":"start","item":"%s"}\n{"t":"end","item":"%s"}\n'%(item,item))
def wakes(calls):
    return [l for l in open(calls) if l.startswith("wake ")]
def say(*a): print(*a)
# ---- Case A: handoff success + one send per action + no duplicate on repeated callback
d,calls=setup("A")
say("== A handoff ==")
say("dispatch",run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","work","--verify-task","verify")[0])
open(os.path.join(d,"art","out.bin"),"w").write("hello")
run(d,"run","--config","cfg.json","--once")
say("wakes after worker dispatch:",len(wakes(calls)))
run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin")
endturn(d,"K","iw1"); run(d,"run","--config","cfg.json","--once")
say("wakes after verifier dispatch:",len(wakes(calls)))
run(d,"claim","--config","cfg.json","--qid","Q1","--step","verify","--outcome","completed","--artifact","out.bin=out.bin")
endturn(d,"C","iv1"); run(d,"run","--config","cfg.json","--once")
st=run(d,"status","--config","cfg.json")[1]
say("status after verify:\n"+st)
run(d,"decide","--config","cfg.json","--qid","Q1","--kind","question_answered","--ref","r1","--reason","ok")
st=run(d,"status","--config","cfg.json")[1]
say("closed?", "closed" in st)
n=len(wakes(calls))
run(d,"timer-callback","--config","cfg.json","--qid","Q1","--action","WRONG","--execution","WRONG")
say("A: wakes total",n,"after bogus callback",len(wakes(calls)),"unchanged:",n==len(wakes(calls)))

# ---- Case B: independence — distinct names, same principal
d,calls=setup("B",seats={"kiln":"K","corvid":"K","tern":"T"})
say("\n== B independence (same principal) ==")
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","work","--verify-task","verify")
open(os.path.join(d,"art","out.bin"),"w").write("hello")
run(d,"run","--config","cfg.json","--once")
run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin")
endturn(d,"K","iwB"); out=run(d,"run","--config","cfg.json","--once")
say("after worker end:",out[1][:200])
st=run(d,"status","--config","cfg.json")[1]; say("status:\n"+st)
# ---- Case C: input validity
d,calls=setup("C")
say("\n== C input validity ==")
open(os.path.join(d,"art","spec.md"),"w").write("v1")
say("missing input dispatch rc:",run(d,"dispatch","--config","cfg.json","--qid","QM","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--input","nope.md")[0:2])
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--input","spec.md")
open(os.path.join(d,"art","out.bin"),"w").write("hello")
run(d,"run","--config","cfg.json","--once")  # worker dispatched
run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin")
w_before=len(wakes(calls))
open(os.path.join(d,"art","spec.md"),"w").write("MUTATED")  # mutate declared input
endturn(d,"K","iwC"); out=run(d,"run","--config","cfg.json","--once")
say("after mutate:",out[1][:200]); say("new wakes:",len(wakes(calls))-w_before)
say("status:\n"+run(d,"status","--config","cfg.json")[1])
# ---- Case D: dependency gate
d,calls=setup("D")
say("\n== D dependency ==")
run(d,"dispatch","--config","cfg.json","--qid","Q1","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v")
open(os.path.join(d,"art","out.bin"),"w").write("hello")
run(d,"run","--config","cfg.json","--once"); run(d,"claim","--config","cfg.json","--qid","Q1","--step","worker","--outcome","completed","--artifact","out.bin=out.bin"); endturn(d,"K","iwD"); run(d,"run","--config","cfg.json","--once")
run(d,"claim","--config","cfg.json","--qid","Q1","--step","verify","--outcome","completed","--artifact","out.bin=out.bin"); endturn(d,"C","ivD"); run(d,"run","--config","cfg.json","--once")
w_before=len(wakes(calls))
say("Q2 dispatch:",run(d,"dispatch","--config","cfg.json","--qid","Q2","--worker","kiln","--verifier","corvid","--task","w","--verify-task","v","--after","Q1")[0:2])
run(d,"run","--config","cfg.json","--once")
say("Q2 wakes while Q1 open:",len(wakes(calls))-w_before)
say("status:\n"+run(d,"status","--config","cfg.json")[1])
run(d,"decide","--config","cfg.json","--qid","Q1","--kind","question_answered","--ref","r1","--reason","ok")
run(d,"run","--config","cfg.json","--once")
say("Q2 wakes after Q1 resolved:",len(wakes(calls))-w_before)
say("final status:\n"+run(d,"status","--config","cfg.json")[1])
