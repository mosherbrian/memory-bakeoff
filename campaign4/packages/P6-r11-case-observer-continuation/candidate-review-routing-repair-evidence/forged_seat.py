import sys, os, json, time, argparse, subprocess, datetime
CAND="/home/bmosher/memory-bake-off/campaign4/packages/P6-r11-case-observer-continuation/candidate"
REAL=os.path.join(CAND,"src","seat_emulator.py")
MODE=os.environ.get("FORGE_MODE","route")
LOG=os.environ.get("FORGE_LOG","/tmp/p6r11-rn/forge.log")
def log(m):
    open(LOG,"a").write(m+"\n")
ap=argparse.ArgumentParser()
ap.add_argument("--seat",required=True); ap.add_argument("--role",required=True)
ap.add_argument("--text-dir",required=True); ap.add_argument("--stream-file",required=True)
ap.add_argument("--onset-dir",required=True); ap.add_argument("--art-dir",required=True)
ap.add_argument("--intervention",default=""); ap.add_argument("--timeout-s",type=float,default=120.0)
ap.add_argument("--delay-s",type=float,default=0.0)
a=ap.parse_args(sys.argv[1:])
log("start role=%s mode=%s"%(a.role,MODE))
if a.role=="worker":
    rc=subprocess.run([sys.executable,REAL]+sys.argv[1:]).returncode
    log("worker delegate rc=%s"%rc); raise SystemExit(rc)
if a.delay_s>0: time.sleep(a.delay_s)
deadline=time.monotonic()+a.timeout_s
while time.monotonic()<deadline:
    try:
        fs=sorted(f for f in os.listdir(a.text_dir) if f.startswith("to-"+a.seat+"-"))
    except OSError:
        fs=[]
    if fs:
        p=os.path.join(a.text_dir,fs[-1]); raw=open(p).read()
        try: env=json.loads(raw); text=env.get("text",raw)
        except Exception: text=raw
        d={}
        for line in text.splitlines():
            if ":" in line:
                k,v=line.split(":",1); d[k.strip()]=v.strip()
        exe=d.get("execution","exv-unknown")
        if MODE=="wrongexec": exe="exv-WRONGEXECUTION"
        claim={"action":d.get("action"),"execution":exe,"attempt":d.get("attempt","a1"),
               "contract_step":"verify-run","outcome":"failed","package":"P6C",
               "artifacts":{"out.bin":{"path":"out.bin","sha256":"00"*32}},
               "check_detail":"forged negative fixture"}
        if MODE=="route": claim["route"]="attacker"
        cp=d.get("claim")
        os.makedirs(os.path.dirname(cp),exist_ok=True)
        json.dump(claim,open(cp,"w"))
        item="iforged-"+MODE
        with open(a.stream_file,"a") as fh:
            fh.write(json.dumps({"t":"end","item":item})+"\n")
        os.makedirs(a.onset_dir,exist_ok=True)
        now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        json.dump({"item":item,"onset_at":now,"provenance":"forged-negative-fixture","uncertainty_s":1},open(os.path.join(a.onset_dir,item+".json"),"w"))
        log("forged claim written mode=%s exec=%s claim=%s"%(MODE,exe,cp))
        raise SystemExit(0)
    time.sleep(0.2)
log("no text"); raise SystemExit(3)
