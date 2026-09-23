"""Tabulate one ack run: per request, detection (earliest trusted: due marker or settlement), settlement, submission,
commit, outcome, lateness. Usage: python ack-analyse.py OUTDIR"""
import json, glob, sys, datetime as D
d = sys.argv[1]
f = lambda s: D.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=D.timezone.utc).timestamp() if s else None
st = {p['qid']: (p.get('timeout') or {}) for p in json.load(open(d + '/status-final.json'))['packages']}
rows = sorted((json.load(open(p)) for p in glob.glob(d + '/acks-store/done/*.json')), key=lambda r: r['qid'])
print('qid by outcome | detection->settlement | submit after detection | commit after detection | commit after submit | late | reason')
worst = 0
for r in rows:
    t = st.get(r['qid'], {}); de = f(r.get('detection')); se = f(t.get('at')); su = f(r['submitted_at']); co = f(r.get('committed_at'))
    g = lambda a, b: None if a is None or b is None else int(a - b)
    if co and su: worst = max(worst, co - su)
    print(r['qid'], r['by'], r['outcome'], '|', g(se, de), '|', g(su, de), '|', g(co, de), '|', g(co, su), '|', r.get('late', False), r.get('late_notice', ''), '|', (r.get('reason') or '')[:100])
print('pending left:', [p.split('/')[-1] for p in glob.glob(d + '/acks-store/*.json')])
print('max commit-after-submit: %ds (declared worst case 25 s while the requester waits; 55 s with run stopped)' % worst)
