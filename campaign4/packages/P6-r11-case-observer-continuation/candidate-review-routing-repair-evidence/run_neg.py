import json,os,sys
sys.path.insert(0,"/tmp/p6r11-rej-repro")
import test_cand as T
REAL=T.R9SEAT
mode=sys.argv[1]
os.environ["FORGE_MODE"]=mode; os.environ["FORGE_LOG"]="/tmp/p6r11-rn/forge-%s.log"%mode
open(os.environ["FORGE_LOG"],"w").close()
env=T.make_suite(T.R9)
T.R9SEAT="/tmp/p6r11-rn/forged_seat.py"
try:
    T.arm(env,"failed-verification","none-declared")
    r=T.run_case(env,"failed-verification",{})
    print("MODE=%s rc=%s"%(mode,r.returncode))
    print("stdout:",r.stdout.strip()[:400])
    print("stderr:",r.stderr.strip()[:200])
finally:
    T.close(env); T.R9SEAT=REAL
