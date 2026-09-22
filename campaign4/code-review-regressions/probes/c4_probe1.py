import os,sys,json,tempfile
H="/home/bmosher/memory-bake-off/campaign4/packages/P6-r9-observer-lifetime/src/r3harness"
sys.path.insert(0,H)
from driver import Driver, FakeClock, FakeExternalWorld
import harness
Q="P6C"; AID="a-w1"
tmp=tempfile.mkdtemp(prefix="c4t1-")
db=os.path.join(tmp,"ledger.db")
d=Driver(db, FakeClock(), FakeExternalWorld(os.path.join(tmp,"world.json")))
d.admit_authorize(Q); d.start_dispatch(Q,AID,duration_s=1); d.acknowledge(AID)
d.close()
# callback argv the harness actually builds (no --qid-cb)
import re
src=open(os.path.join(H,"harness.py")).read()
m=re.search(r"cb = \[(.*?)\]", src, re.S)
print("callback argv template contains --qid-cb:", "--qid-cb" in m.group(1))
r_default=harness.timer_callback(db,"p6-stagec-h1",action_id=AID)          # default qid P6F
r_correct=harness.timer_callback(db,"p6-stagec-h1",qid=Q,action_id=AID)     # P6C
print("default-qid callback:",r_default)
print("P6C-qid callback:",r_correct)
