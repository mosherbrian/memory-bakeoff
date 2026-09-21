"""Run with PYTHONPATH=<candidate>/src; disposable fake-only stores."""
import json,tempfile
from pathlib import Path
from driver import Driver,FakeClock,FakeExternalWorld
p=Path(tempfile.mkdtemp(prefix='p5-director-'))
d=Driver(str(p/'s.db'),FakeClock(),FakeExternalWorld(str(p/'w.json')))
results={}
def probe(name,fn):
 try: results[name]={'accepted':True,'result':fn()}
 except Exception as e: results[name]={'accepted':False,'error':getattr(e,'code',type(e).__name__)}
probe('caller_actor',lambda:d.ingress.append({'event_id':'forged-reader','question_id':'Q','revision':1,'type':'admit','actor':{'seat':'kiln','role':'reader'}},d.budget,grants=d.grants))
d.admit_authorize('V');d.start_dispatch('V','w',duration_s=60)
probe('ungranted_verifier_deadline',lambda:d.publish_completion('V','w',{'x':'h'},verify={'action_id':'v','owner':'corvid','deadline':'2099-01-01T00:00:00Z'}))
results['flight']=d.store.revisions[('V',1)]['flight']
d.admit_authorize('G');d.pin_grant('wrong-phase','2026-09-21T14:00:00Z',phase='CHECKING')
probe('wrong_phase_grant_without_hint',lambda:d.start_dispatch('G','wg',grant_ref='wrong-phase'))
e=d.ingress.epoch;d.close()
d=Driver(str(p/'s.db'),FakeClock(),FakeExternalWorld(str(p/'w.json')))
results['restart_epoch_reused']=e==d.ingress.epoch
d.close();print(json.dumps(results,indent=2))
