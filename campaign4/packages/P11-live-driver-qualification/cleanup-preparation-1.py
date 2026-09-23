import json,os,subprocess,sys,datetime
from pathlib import Path
PLAN=Path(__file__).with_name('preparation-release-1.json')
p=json.loads(PLAN.read_text());env=dict(os.environ,AGENTDECK_PROFILE=p['profile'])
sessions=json.loads(subprocess.check_output(['agent-deck','-p',p['profile'],'list','--json'],env=env))
owned=[]
for role in p['roles']:
 matches=[s for s in sessions if s.get('title')==role['name'] and os.path.realpath(s.get('path',''))==os.path.realpath(role['workdir']) and s.get('command')==role['lane'] and s.get('profile')==p['profile']]
 if len(matches)>1:raise SystemExit('ambiguous owned binding; refuse cleanup')
 owned+=matches
main={'0c933c75-1790000758','493c0317-1790000758','a79067ca-1790000758','56513e0e-1790000758'}
if any(s['id'] in main for s in owned):raise SystemExit('main seat forbidden')
a=PLAN.parent/'live-preparation-1'/'cleanup-archive';a.mkdir(parents=True,exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
(a/(stamp+'-registry.json')).write_text(json.dumps(owned,indent=2)+'\n')
results=[]
for s in owned:
 for op in ('stop','remove'):
  r=subprocess.run(['agent-deck','session',op,s['id']],env=env,text=True,capture_output=True,timeout=60)
  results.append(dict(id=s['id'],op=op,rc=r.returncode,stdout=r.stdout,stderr=r.stderr))
(a/(stamp+'-results.json')).write_text(json.dumps(results,indent=2)+'\n')
if any(r['rc'] for r in results):raise SystemExit(3)
