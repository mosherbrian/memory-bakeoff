"""PYTHONPATH=<candidate>/src:<candidate>/tests python3 this-file; fake only."""
from test_repair2_atomic import mk, checking, Q, DISP
import json
d = mk(); checking(d)
v = dict(event_id='mixed-v', question_id=Q, revision=1, type='verify_pass',
         elapsed_s=60, pass_budget_s=1800, finding='positive')
s = dict(event_id='mixed-d', question_id=Q, revision=1, type='decide',
         actor={'seat':'kiln','role':'director'}, at='2099-01-01T00:00:00Z',
         disposition=dict(DISP))
try:
    result = d.ingress.append(v,d.budget,
        atomic={'hold':'2026-09-21T15:00:00Z','decide':s},
        grants=d.grants,actor={'seat':'corvid','role':'verifier'})
    print('ACCEPTED',result)
except Exception as e:
    print('REJECTED',getattr(e,'code',type(e).__name__))
print(json.dumps(d.store.conn.execute(
    "select event_id,actor_seat,actor_role,at,body from events "
    "where event_id in ('mixed-v','mixed-d')").fetchall()))
d.close()
