"""Independent #11 identity probe (private temp DBs). NEWC from argv[1]."""
import os, sys, json, tempfile, hashlib
NEWC=sys.argv[1]
sys.path.insert(0, NEWC)
import lifecycle as LC, store as STOREMOD
from driver import Driver, FakeClock, FakeExternalWorld
Q="C4I"
KILN_W={"seat":"kiln","role":"worker"}; KILN_V={"seat":"kiln","role":"verifier"}
CORVID_V={"seat":"corvid","role":"verifier"}
DIR={"seat":"tern","role":"director"}
DISP={"kind":"question_answered","decision_ref":"t-1","reason":"ok","evidence_refs":["h"]}
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def mk():
    t=tempfile.mkdtemp(prefix="c4i-"); d=Driver(os.path.join(t,"l.db"),FakeClock(),FakeExternalWorld(os.path.join(t,"w.json"))); d.tmp=t; return d
def published(d,aid="a-w1"):
    d.admit_authorize(Q); d.start_dispatch(Q,aid,duration_s=3600); d.acknowledge(aid)
    d.publish_completion(Q,aid,{"h":"x"},verify={"action_id":"a-v1","owner":"corvid","deadline":"2026-09-21T14:00:00Z"})
def counts(d): return (d.store.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0], set(d.store.seen_events), d.store.revisions[(Q,1)]["phase"])
def vclaim(eid,typ="verify_pass",extra=None):
    e={"event_id":eid,"question_id":Q,"revision":1,"type":typ,"elapsed_s":60,"pass_budget_s":1800,"finding":"positive"}
    e.update(extra or {}); return e
def submit(d,eid,actor,typ="verify_pass",atomic=None,extra=None):
    aa=None if atomic is None or "hold" in atomic else dict(DIR)
    return d.ingress.append(vclaim(eid,typ,extra),d.budget,atomic,getattr(d,"grants",None),actor=dict(actor),atomic_actor=aa)
print("modules:",os.path.basename(NEWC),sha(LC.__file__)[:12],sha(STOREMOD.__file__)[:12])
# same-principal verify_pass and verify_fail, plain and atomic
for typ in ("verify_pass","verify_fail"):
    d=mk()
    try:
        published(d); before=counts(d)
        try:
            submit(d,"ev-"+typ,KILN_V,typ); r="ACCEPTED"
        except Exception as e: r="rejected %s"%getattr(e,"code",type(e).__name__)
        print("same-principal %-11s -> %s ; zero-change=%s"%(typ,r,counts(d)==before))
    finally: d.close()
# atomic decide
d=mk()
try:
    published(d); before=counts(d)
    dec={"event_id":"ev-d","question_id":Q,"revision":1,"type":"decide","at":"2026-09-21T12:10:00Z","disposition":dict(DISP)}
    try: submit(d,"ev-vp",KILN_V,"verify_pass",atomic={"decide":dec}); r="ACCEPTED"
    except Exception as e: r="rejected %s"%getattr(e,"code",type(e).__name__)
    print("same-principal + atomic decide ->",r,"; zero-change=",counts(d)==before)
finally: d.close()
# adversarial claimed worker_seat override on the verify event
d=mk()
try:
    published(d)
    try: submit(d,"ev-adv",KILN_V,"verify_pass",extra={"worker_seat":"corvid"}); r="ACCEPTED"
    except Exception as e: r="rejected %s"%getattr(e,"code",type(e).__name__)
    print("claimed worker_seat override ->",r)
finally: d.close()
# distinct legitimate verifier
d=mk()
try:
    published(d)
    dec={"event_id":"ev-d2","question_id":Q,"revision":1,"type":"decide","at":"2026-09-21T12:10:00Z","disposition":dict(DISP)}
    submit(d,"ev-cv",CORVID_V,"verify_pass",atomic={"decide":dec})
    rec=d.store.revisions[(Q,1)]
    print("distinct verifier -> phase",rec["phase"],"disposition",bool(rec.get("disposition")),"producer_seat",rec.get("producer_seat"))
    # reopen preserves
    db=d.store.path; d.close()
    d2=Driver(db,FakeClock(),FakeExternalWorld(os.path.join(d.tmp,"w.json")))
    print("reopen producer_seat",d2.store.revisions[(Q,1)].get("producer_seat"))
    d=d2
finally: d.close()
# missing producer identity (internal invariant)
st=LC.new_revision(Q); st["phase"]="CHECKING"
try:
    LC.apply(st,{"event_id":"x","type":"verify_pass","actor":{"seat":"corvid","role":"verifier"},"elapsed_s":60,"pass_budget_s":1800,"finding":"positive"},"2026-09-21T12:00:00Z",{})
    print("missing producer -> ACCEPTED")
except Exception as e: print("missing producer -> rejected",getattr(e,"code",type(e).__name__))
