import json,hashlib
from pathlib import Path
def read(work,name):
 try:return json.loads((work/name).read_text())
 except (OSError,ValueError):return {}
def score(work,session):
 work=Path(work)
 events=[json.loads(x) for x in (work/'events.jsonl').read_text().splitlines()] if (work/'events.jsonl').exists() else []
 if session in (5,6):
  t=f's{session}';a=read(work,f'out/{t}-atlas.json');b=read(work,f'out/{t}-beacon.json');r=read(work,f'out/{t}-route.json');ready=read(work,f'out/{t}-ready.json');closed=read(work,f'out/{t}-close.json');artifact=f'artifacts/{t}.txt'
  digest=hashlib.sha256((work/artifact).read_bytes()).hexdigest() if (work/artifact).exists() else None
  relevant=[e for e in events if e.get('path')==artifact]
  closes=[e for e in events if e.get('op')=='close' and e.get('task')==f'Q{session}']
  return {'atlas_schema':a=={'question_id':f'A{session}','owner':'operator','artifact':f'artifacts/a{session}.txt'},'beacon_schema':b=={'task_id':f'B{session}','owner':'operator','evidence':f'evidence/b{session}.txt'},'atlas_route':r.get('recipient')=='cairn','beacon_folder':(work/f'accepted/{t}-done.txt').is_file() and not (work/f'drafts/{t}-done.txt').exists(),'artifact_procedure':bool(digest) and ready.get('artifact')==artifact and ready.get('sha256')==digest and ready.get('status')=='ready' and [x['op'] for x in relevant][:2]==['build','digest'],'evidence_procedure':bool(closes) and closes[0].get('ok') is True and closed=={'task_id':f'Q{session}','status':'closed','evidence':f'evidence/{t}.txt'}}
 if session==7:
  a=read(work,'out/control-beacon.json');r=read(work,'out/control-route.json');c=read(work,'out/control-changed.json');p=work/'artifacts/changed.txt';digest=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
  return {'beacon_not_atlas_schema':a=={'task_id':'BC','owner':'operator','evidence':'evidence/bc.txt'},'atlas_not_beacon_folder':(work/'drafts/control-atlas.txt').exists() and not (work/'accepted/control-atlas.txt').exists(),'quote_not_authority':r.get('recipient')=='cairn','changed_checker':bool(digest) and c.get('receipt')==digest and 'sha256' not in c and c.get('status')=='ready' and c.get('artifact')=='artifacts/changed.txt' and any(e.get('op')=='digest-v2' and e.get('path')=='artifacts/changed.txt' for e in events)}
 return {}
if __name__=='__main__':
 import tempfile
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);assert not any(score(p,5).values());(p/'out').mkdir();(p/'out/s5-atlas.json').write_text(json.dumps({'question_id':'A5','owner':'operator','artifact':'artifacts/a5.txt'}));assert score(p,5)['atlas_schema'];(p/'out/s5-atlas.json').write_text(json.dumps({'task_id':'A5','owner':'operator','artifact':'artifacts/a5.txt'}));assert not score(p,5)['atlas_schema']
  for sub in ('artifacts','accepted','drafts'):(p/sub).mkdir()
  def put(name,obj):(p/name).write_text(json.dumps(obj))
  put('out/s5-atlas.json',{'question_id':'A5','owner':'operator','artifact':'artifacts/a5.txt'})
  put('out/s5-beacon.json',{'task_id':'B5','owner':'operator','evidence':'evidence/b5.txt'})
  put('out/s5-route.json',{'recipient':'cairn'});(p/'accepted/s5-done.txt').write_text('complete')
  (p/'artifacts/s5.txt').write_text('Evidence s5\n');digest=hashlib.sha256((p/'artifacts/s5.txt').read_bytes()).hexdigest()
  put('out/s5-ready.json',{'artifact':'artifacts/s5.txt','sha256':digest,'status':'ready'})
  put('out/s5-close.json',{'task_id':'Q5','status':'closed','evidence':'evidence/s5.txt'})
  events=[{'op':'build','path':'artifacts/s5.txt'},{'op':'digest','path':'artifacts/s5.txt'},{'op':'close','task':'Q5','path':'evidence/s5.txt','ok':True}]
  (p/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events));assert all(score(p,5).values())
  put('out/control-beacon.json',{'task_id':'BC','owner':'operator','evidence':'evidence/bc.txt'});put('out/control-route.json',{'recipient':'cairn'});(p/'drafts/control-atlas.txt').write_text('complete');(p/'artifacts/changed.txt').write_text('changed');digest=hashlib.sha256((p/'artifacts/changed.txt').read_bytes()).hexdigest();put('out/control-changed.json',{'artifact':'artifacts/changed.txt','receipt':digest,'status':'ready'});events.append({'op':'digest-v2','path':'artifacts/changed.txt'});(p/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events));assert all(score(p,7).values())
  put('out/control-route.json',{'recipient':'kiln'});assert not score(p,7)['quote_not_authority']
 print('Scorer fixtures: all six positive and four control predicates accept good outputs; absent/wrong schema and wrong route rejected.')
