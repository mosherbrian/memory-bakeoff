"""C4 regressions probes: P5-r2 durable-record findings 2,5,6,7,10.

Pinned source: campaign4/packages/P5-r2-atomic-authority/src (store.py
dafaeb33, ingress.py c9327f85, lifecycle.py 7ebaf466). Private temp DBs only.
"""
import os, sys, json, tempfile, traceback
SRC="/home/bmosher/memory-bake-off/campaign4/packages/P5-r2-atomic-authority/src"
sys.path.insert(0, SRC)
from driver import Driver, FakeClock, FakeExternalWorld
from lifecycle import apply, new_revision, TransitionError
Q="C4T"
DISP={"kind":"question_answered","decision_ref":"t-1","reason":"ok","evidence_refs":["h"]}

def mk():
    tmp=tempfile.mkdtemp(prefix="c4-")
    d=Driver(os.path.join(tmp,"ledger.db"), FakeClock(), FakeExternalWorld(os.path.join(tmp,"world.json")))
    d.tmp=tmp; return d

def checking(d, aid="a-w1"):
    d.admit_authorize(Q)
    d.start_dispatch(Q, aid, duration_s=3600)
    d.acknowledge(aid)
    d.publish_completion(Q, aid, {"h":"x"}, verify={"action_id":"a-v1","owner":"corvid","deadline":"2026-09-21T14:00:00Z"})

def ev(eid,typ,who,role,body=None):
    e={"event_id":eid,"question_id":Q,"revision":1,"type":typ,"actor":{"seat":who,"role":role},"at":"2026-09-21T12:10:00Z"}
    e.update(body or {}); return e

results={}
def rec(n,status,detail):
    results[n]=(status,detail); print("[%s] %s :: %s"%(status,n,detail))

# ---- #6 second DECIDE overwrites first (pure core) ----
try:
    st=new_revision(Q); st["phase"]="COMPLETE"
    st,_=apply(st, ev("d1","decide","tern","director",{"disposition":dict(DISP,reason="first")}), "2026-09-21T12:00:00Z", {})
    first=st["disposition"]["reason"]
    st,_=apply(st, ev("d2","decide","tern","director",{"disposition":dict(DISP,reason="second")}), "2026-09-21T12:01:00Z", {})
    second=st["disposition"]["reason"]
    rec(6, "REPRODUCED" if (first=="first" and second=="second") else "NOT REPRODUCED",
        "two DECIDE on COMPLETE: disposition reason %r -> %r (no 'already closed' rejection)"%(first,second))
except Exception as e:
    rec(6,"UNTESTED","exc %r"%e)

# ---- #10 deadline compared as text ----
try:
    st=new_revision(Q); st["phase"]="RUNNING"; st["deadline"]="2026-09-22T22:00:00+02:00"
    # instant: deadline=20:00Z, now=20:30Z -> expired; lexicographic: now<deadline -> not expired
    try:
        st2,out=apply(st, ev("p1","publish","alpha-12","worker",
            {"artifact_hashes":{"h":"x"},"verify":{"action_id":"a-v1","owner":"corvid","deadline":"2026-09-23T00:00:00Z"}}),
            "2026-09-22T20:30:00Z", {})
        rec(10,"REPRODUCED","PUBLISH accepted (phase %s) though instant 20:30Z > deadline 20:00Z; text compare now=%r vs deadline=%r"%(st2["phase"],"2026-09-22T20:30:00Z",st["deadline"]))
    except TransitionError as e:
        rec(10,"NOT REPRODUCED","rejected %s"%e)
except Exception as e:
    rec(10,"UNTESTED","exc %r"%e)

# ---- #2 record_terminal leaves verdict in seen_events after rollback ----
try:
    d=mk(); checking(d)
    existing=d.store.conn.execute("SELECT event_id FROM events ORDER BY rowid LIMIT 1").fetchone()[0]
    verdict=ev("ev-vp-c4","verify_pass","corvid","verifier",{"elapsed_s":60,"pass_budget_s":1800,"finding":"positive"})
    decide=ev(existing,"decide","tern","director",{"disposition":dict(DISP)})
    try:
        d.store.record_terminal(verdict, decide)
        rec(2,"NOT REPRODUCED","record_terminal did not raise on duplicate decide")
    except TransitionError as e:
        seen = "ev-vp-c4" in d.store.seen_events
        persisted=d.store.conn.execute("SELECT COUNT(*) FROM events WHERE event_id='ev-vp-c4'").fetchone()[0]
        # retry with a fresh decide id
        decide2=ev("ev-dec-c4-fresh","decide","tern","director",{"disposition":dict(DISP)})
        try:
            d.store.record_terminal(verdict, decide2); retry="committed"
        except TransitionError as e2:
            retry="raised %s"%e2.code
        rec(2, "REPRODUCED" if (seen and persisted==0 and retry!="committed") else "NOT REPRODUCED",
            "first=%s seen_after_rollback=%s persisted=%s retry_with_fresh_decide=%s"%(e.code,seen,persisted,retry))
    d.close()
except Exception as e:
    rec(2,"UNTESTED","exc %r"%traceback.format_exc()[-200:])

# ---- #7 decide + grant_ref accepted (ingress) ----
try:
    d=mk(); checking(d)
    v=ev("ev-vp-g","verify_pass","corvid","verifier",{"elapsed_s":60,"pass_budget_s":1800,"finding":"positive"})
    sub={"event_id":"ev-dec-g","question_id":Q,"revision":1,"type":"decide","at":"2026-09-21T12:10:00Z","disposition":dict(DISP)}
    try:
        d.ingress.append(v, d.budget, atomic={"decide":sub,"grant_ref":"g-forged"}, grants=getattr(d,"grants",None))
        rec(7,"REPRODUCED","atomic decide+grant_ref accepted (grant_ref silently stripped); disposition=%s"%(d.store.revisions[(Q,1)].get("disposition") is not None))
    except Exception as e:
        rec(7,"NOT REPRODUCED","rejected %s: %s"%(getattr(e,'code',type(e).__name__),e))
    d.close()
except Exception as e:
    rec(7,"UNTESTED","exc %r"%traceback.format_exc()[-200:])

print(json.dumps(results, indent=1))
