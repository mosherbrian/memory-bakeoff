"""Score every returned predeclared case, without model calls or threshold tuning."""
import json, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cases=[json.loads(x) for x in (ROOT/'cases.jsonl').read_text().splitlines()]
replies={r['id']:r for r in map(json.loads,(ROOT/'responses.jsonl').read_text().splitlines())}
rows=[]
for c in cases:
    if c['id'] not in replies: continue
    r=replies[c['id']]; p=r['reply']['answers']['superseded']['noul']
    rows.append(dict(id=c['id'],family=c['family'],gold=c['gold'],p=p,prediction=p>=.5,correct=(p>=.5)==c['gold'],elapsed_seconds=r['elapsed_seconds']))
def metrics(items,method):
    cm=dict(tp=0,tn=0,fp=0,fn=0)
    for r in items:
        pred = r['prediction'] if method=='laya' else (False if method=='majority_no' else next(c['rule_prediction'] for c in cases if c['id']==r['id']))
        key=('t' if pred==r['gold'] else 'f')+('p' if pred else 'n'); cm[key]+=1
    return dict(n=len(items),correct=cm['tp']+cm['tn'],accuracy=(cm['tp']+cm['tn'])/len(items) if items else None,**cm)
bins=[]
for i in range(5):
    part=[r for r in rows if min(4,int(r['p']*5))==i]
    bins.append(dict(lower=i/5,upper=(i+1)/5,n=len(part),mean_p=statistics.mean(r['p'] for r in part) if part else None,observed_yes=statistics.mean(r['gold'] for r in part) if part else None))
select=[r for r in rows if r['p']<=.1 or r['p']>=.9]
lat=sorted(r['elapsed_seconds'] for r in rows)
summary=dict(expected=46,scored=len(rows),metrics={m:metrics(rows,m) for m in ['laya','majority_no','whole_token_rule']},brier=statistics.mean((r['p']-r['gold'])**2 for r in rows) if rows else None,ece5=sum(b['n']*abs(b['mean_p']-b['observed_yes']) for b in bins if b['n'])/len(rows) if rows else None,bins=bins,selective=dict(coverage=len(select)/len(rows) if rows else None,**metrics(select,'laya')),families={f:{m:metrics([r for r in rows if r['family']==f],m) for m in ['laya','majority_no','whole_token_rule']} for f in sorted({r['family'] for r in rows})},latency=dict(first=rows[0]['elapsed_seconds'] if rows else None,median=statistics.median(lat) if lat else None,p95=lat[min(len(lat)-1,int(.95*len(lat)))] if lat else None,total=sum(lat),remaining_median=statistics.median(r['elapsed_seconds'] for r in rows[1:]) if len(rows)>1 else None),failures=[r for r in rows if not r['correct']])
(ROOT/'scores.json').write_text(json.dumps(summary,indent=2)+'\n')
(ROOT/'scored-cases.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
print(json.dumps(summary,indent=2))
