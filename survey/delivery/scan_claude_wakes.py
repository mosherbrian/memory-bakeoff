from pathlib import Path
from datetime import datetime,timezone
import json,re,hashlib,collections
st=datetime.fromisoformat('2026-09-19T19:55:00+00:00').timestamp();en=st+604800
base=Path('/var/home/bmosher/.claude/projects');files=[p for p in base.rglob('*.jsonl') if p.stat().st_mtime>=st]
rows={};requests={};results={};scanned=0
pattern=re.compile(r'(?:^|[\s;/])(?:wake|wake-session)(?:\s|$)')
strong=re.compile(r'\b(?:you (?:are|went|remain) idle|still idle|rest.{0,50}expired|resume|stalled|keep running|no.idling|do not idle|don.t stop|continue.{0,35}now)\b',re.I)
for p in files:
 for ln,line in enumerate(p.open(),1):
  try:r=json.loads(line)
  except:continue
  ts=r.get('timestamp')
  if not isinstance(ts,str):continue
  try:t=datetime.fromisoformat(ts.replace('Z','+00:00')).timestamp()
  except ValueError:continue
  if not st<=t<en:continue
  scanned+=1;m=r.get('message',{});content=m.get('content',[])
  if not isinstance(content,list):continue
  for b in content:
   if not isinstance(b,dict):continue
   if b.get('type')=='tool_use' and b.get('name')=='Bash':
    cmd=b.get('input',{}).get('command','')
    if not isinstance(cmd,str) or not pattern.search(cmd):continue
    k=b.get('id');item={'tool_use_id':k,'source':str(p),'line':ln,'at':ts,'command_hash':hashlib.sha256(cmd.encode()).hexdigest(),'strong_nudge_candidate':bool(strong.search(cmd))}
    rows[k]=item;requests[k]=cmd
   elif b.get('type')=='tool_result':
    raw=b.get('content','');txt=raw if isinstance(raw,str) else json.dumps(raw)
    results[b.get('tool_use_id')]={'is_error':bool(b.get('is_error',False)),'wake_ack':bool(re.search(r'wake: .{1,80}-> (started|queued)',txt))}
for k,v in rows.items():v['result']=results.get(k,{'missing':True})
d={'files_scanned':len(files),'rows_in_window':scanned,'wake_command_candidates':len(rows),'strong_nudge_candidates':sum(x['strong_nudge_candidate'] for x in rows.values()),'candidates':list(rows.values()),'scope':'Claude Bash tool-use records, windowed; command regex candidates require intent review. No private command text published.'}
out=Path('survey/delivery/claude-wake-candidates-20260926.json');out.write_text(json.dumps(d,indent=2)+'\n')
private=Path('/tmp/tern-fleet-baseline-20260926/claude-wake-candidate-text.json');private.write_text(json.dumps(requests));private.chmod(0o600)
print(json.dumps({k:v for k,v in d.items() if k!='candidates'},indent=2))
print('acknowledged strong nudges',sum(x['strong_nudge_candidate'] and x['result'].get('wake_ack',False) for x in rows.values()))
