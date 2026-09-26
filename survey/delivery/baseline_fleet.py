"""Offline seven-day baseline from existing local logs; no service or model calls.
Raw snapshots stay in a mode-0700 directory outside the repository.
"""
import argparse, collections, hashlib, json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--end',default='2026-09-26T19:55:00+00:00')
ap.add_argument('--out',default='survey/delivery/fleet-baseline-20260926.json')
ap.add_argument('--snapshot',default='/tmp/tern-fleet-baseline-20260926')
a=ap.parse_args(); end=datetime.fromisoformat(a.end).timestamp();start=end-7*86400
root=Path('/var/home/bmosher/.local/share/agent-deck');snap=Path(a.snapshot);snap.mkdir(mode=0o700,parents=True,exist_ok=True);snap.chmod(0o700)
def iso(t):return datetime.fromtimestamp(t,timezone.utc).isoformat()
def within(t):return start<=t<end
manifest=[]
def read(rel):
 p=root/rel;dest=snap/Path(rel).name
 if not dest.exists():dest.write_bytes(p.read_bytes());dest.chmod(0o600)
 b=dest.read_bytes();manifest.append({'source':str(p),'snapshot':str(dest),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
 return b.decode().splitlines()
esc=[json.loads(x) for x in read('escalations.jsonl') if x.strip()]
events=[r for r in esc if 'id' in r and within(r['t'])]
seen=set();ev=[]
for r in events:
 key=r.get('key',r['id'])
 if key not in seen:ev.append(r);seen.add(key)
gap_re=re.compile(r'GAP-(Q-[A-Z-]+)-(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)')
gaps={}; unmatched=[]
for r in ev:
 if r.get('kind')!='research-gap':continue
 m=gap_re.search(r.get('text',''))
 if not m:unmatched.append(r['id']);continue
 g=gaps.setdefault(m[0],{'question':m[1],'start':datetime.fromisoformat(m[2].replace('Z','+00:00')).timestamp(),'notification_ids':[],'keys':[]})
 g['notification_ids'].append(r['id']);g['keys'].append(r['key'])
for incident,g in gaps.items():
 close=[r['t'] for r in esc if r.get('resolve') in g['keys'] and r.get('incident')==incident and g['start']<=r['t']<end]
 g['resolved_at']=min(close) if close else None
 g['observed_minutes_until_resolution']=(g['resolved_at']-max(start,g['start']))/60 if close else None
for g in gaps.values():g['start']=iso(g['start']);g['resolved_at']=iso(g['resolved_at']) if g['resolved_at'] else None

wakes=[]
for line in read('wake-send.log'):
 c=line.split('\t')
 if len(c)<7:continue
 t=datetime.fromisoformat(c[0].replace('Z','+00:00')).timestamp()
 if within(t):wakes.append({'at':c[0],'status':c[4],'sender':c[6],'target':c[2]})
util=sorted((json.loads(x) for x in read('logs/utilization.jsonl') if x.strip()),key=lambda r:r['at'])
covered=idle=lanes=active=allidle=0.;gaps_over60=0
for i,r in enumerate(util):
 nxt=util[i+1]['at'] if i+1<len(util) else end
 lo=max(start,r['at']);hi=min(end,nxt,r['at']+60)
 if hi<=lo:continue
 assert 0<=r['a']<=r['n'],r
 seconds=hi-lo;covered+=seconds;lanes+=r['n']*seconds;active+=r['a']*seconds;idle+=(r['n']-r['a'])*seconds
 if r['a']==0 and r['n']>0:allidle+=seconds
 if within(r['at']) and nxt-r['at']>60:gaps_over60+=1

# Explicit sender markers only. Keyword hits are candidate interventions, not gold.
histroot=Path('/var/home/bmosher/.config/agent-deck/acp-history');hmanifest=[];candidates=[];attributed=0;user_events=0
marker=re.compile(r'^\s*\[(?:Claude(?: for Brian)?|from Brian.s Claude|Brian)\]',re.I)
nudge=re.compile(r'\b(wake|nudge|idle|resume|continue|keep running|stalled|no.idling)\b',re.I)
for p in sorted(histroot.glob('*.jsonl')):
 h=hashlib.sha256();count=0;first=last=None
 with p.open('rb') as fh:
  for lineno,line in enumerate(fh,1):
   h.update(line)
   try:r=json.loads(line)
   except (ValueError,UnicodeDecodeError):continue
   t=r.get('at',0)
   if not isinstance(t,(int,float)) or not within(t):continue
   count+=1;first=t if first is None else min(first,t);last=t if last is None else max(last,t)
   if r.get('role')!='user':continue
   user_events+=1;text=r.get('text','')
   if not isinstance(text,str) or not marker.match(text):continue
   attributed+=1
   if nudge.search(text):candidates.append({'source':str(p),'line':lineno,'at':iso(t),'message_sha256':hashlib.sha256(text.encode()).hexdigest(),'status':'marker_plus_keyword_candidate'})
 if count:hmanifest.append({'source':str(p),'sha256':h.hexdigest(),'window_rows':count,'first':iso(first),'last':iso(last)})
classes=collections.Counter()
for incident,g in gaps.items():classes['research-gap / '+g['question']]+=1
for r in ev:
 if r['kind'] in {'wake-failed','unit-failed','coax','failover','stalled','verifier-dark'}:classes[r['kind']+' / '+r.get('source','unknown')]+=1
out={'window':{'start_inclusive':iso(start),'end_exclusive':iso(end),'days':7,'cutoff_reason':'Frozen before c85 commission wakes; UTC window'},'source_manifest':manifest,'history_manifest':hmanifest,
'manual_interventions':{'total':'unknown','reason':'Most wake senders missing; history may omit caller provenance. Do not count all wakes as manual.','attributed_history_messages':attributed,'history_user_events':user_events,'candidate_count':len(candidates),'candidates':candidates},
'wakes':{'observed':len(wakes),'senders':dict(collections.Counter(r['sender'] for r in wakes)),'statuses':dict(collections.Counter(r['status'] for r in wakes)),'first_observed':wakes[0]['at'] if wakes else None,'last_observed':wakes[-1]['at'] if wakes else None},
'gap_alarms':{'notification_events':sum(r['kind']=='research-gap' for r in ev),'unique_incidents':len(gaps),'unmatched_ids':unmatched,'incidents':gaps,'explicitly_resolved':sum(g['resolved_at'] is not None for g in gaps.values()),'known_resolution_minutes':round(sum(g['observed_minutes_until_resolution'] or 0 for g in gaps.values()),2),'unresolved_duration':'unknown, not counted as ongoing idleness'},
'idle':{'observed_lane_minutes':round(idle/60,2),'observed_total_lane_minutes':round(lanes/60,2),'inactive_share':round(idle/lanes,4) if lanes else None,'all_observed_lanes_inactive_wall_minutes':round(allidle/60,2),'sampled_wall_minutes':round(covered/60,2),'window_wall_minutes':10080,'missing_wall_minutes':round((end-start-covered)/60,2),'sampling_gaps_over_60s':gaps_over60,'interpretation':'Non-active lane-time, not proven avoidable idle. Aggregates lack seat IDs, ready-work, quota and valid-rest state. Hold each sample at most60s; missing intervals excluded.'},
'recurrence':{'definition':'Distinct alert fingerprints grouped by existing operational kind/source (research gaps use incident IDs and question); repeats are fingerprints after first in window. Not semantic same-cause proof.','episodes_by_class':dict(classes),'repeated_episodes':sum(max(0,n-1) for n in classes.values()),'classes_repeated':sum(n>1 for n in classes.values())},
'escalation_coverage':{'first_ledger_row':iso(min(r['t'] for r in esc)),'last_ledger_row':iso(max(r['t'] for r in esc)),'unique_window_events':len(ev)}}
Path(a.out).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k in ['window','wakes','idle','recurrence','escalation_coverage']},indent=2))
print('manual candidates',len(candidates),'gap notifications',out['gap_alarms']['notification_events'],'incidents',len(gaps),'resolved',out['gap_alarms']['explicitly_resolved'])
