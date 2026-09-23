import os,sys,json,time,subprocess,hashlib,shutil,datetime,stat
from pathlib import Path
P=Path(__file__).resolve().parent; C=P/'live-config-1.json';cfg=json.loads(C.read_text());B=cfg['bin'];R=Path(cfg['db']).parent;E=P/'live-1';E.mkdir(exist_ok=True);env=dict(os.environ,AGENTDECK_PROFILE='campaign4');seq=0;proc=None
sig=json.loads((P/'live-signature-1.json').read_text())
now=lambda:datetime.datetime.now(datetime.timezone.utc)
def call(argv,check=True,timeout=45):
 global seq
 seq+=1;r=subprocess.run(argv,capture_output=True,text=True,env=env,timeout=timeout)
 (E/(str(seq).zfill(3)+'-command.json')).write_text(json.dumps(dict(at=now().isoformat(),argv=argv,rc=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n')
 if check and r.returncode:raise RuntimeError(str(argv)+' rc '+str(r.returncode))
 return r

def cli(*args,**kw):return call([B,*args,'--config',str(C)],**kw)
def status():return json.loads(cli('status','--json').stdout)
def wait_step(qid,wanted,bound):
 until=time.monotonic()+bound
 while time.monotonic()<until:
  rows=status()['packages'];row=next((x for x in rows if x['qid']==qid),None)
  if row and row['step'] in wanted:return row
  if row and row['step'] in ('blocked','recovery','timed-out','closed'):
   raise RuntimeError('unexpected state '+str(row))
  time.sleep(5)
 raise RuntimeError('bounded observation expired '+qid)
def start():
 global proc
 log=open(E/('run-'+str(seq)+'.log'),'a');proc=subprocess.Popen([B,'run','--config',str(C)],stdout=log,stderr=subprocess.STDOUT,env=env);log.close()
def stop():
 global proc
 if proc:
  cli('stop',check=False)
  try:proc.wait(timeout=40)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=10)
  proc=None
result={'state':'INCOMPLETE','started_at':now().isoformat()}
try:
 if now()>datetime.datetime.fromisoformat(sig['start_not_after']):raise RuntimeError('signature start expired')
 for name,want in sig['hashes'].items():
  if hashlib.sha256((P/name).read_bytes()).hexdigest()!=want:raise RuntimeError('signed file drift '+name)
 if hashlib.sha256(Path(B).read_bytes()).hexdigest()!=sig['binary_sha256']:raise RuntimeError('binary drift')
 binding=json.loads((P/'execution-binding-1.json').read_text());reg=json.loads(call(['agent-deck','-p','campaign4','list','--json']).stdout)
 for x in binding['roles'].values():
  s=next(s for s in reg if s['id']==x['session_id']);st=os.stat(x['socket'])
  if s['title']!=x['name'] or s['command']!=x['lane'] or not stat.S_ISSOCK(st.st_mode) or st.st_ino!=x['inode'] or st.st_mtime_ns!=x['mtime_ns']:raise RuntimeError('binding drift')
 if call(['systemctl','--user','is-active','campaign4-p8-prep1-cleanup.timer']).stdout.strip()!='active':raise RuntimeError('cleanup not active')
 cli('check');start();w=binding['roles']['worker']['name'];v=binding['roles']['verifier']['name']
 cli('dispatch','--qid','P8-positive-1','--worker',w,'--verifier',v,'--task','@'+str(P/'live-worker-task-1.txt'),'--verify-task','@'+str(P/'live-verifier-task-1.txt'),'--duration','300s','--verify-window','300s')
 row=wait_step('P8-positive-1',{'decision'},650)
 if row['verdict']!='PASS':raise RuntimeError('genuine verification did not pass')
 cli('decide','--qid','P8-positive-1','--kind','question_answered','--ref','P8-live1-signed','--reason','real fixture hash verified')
 stop();start();time.sleep(35);row=wait_step('P8-positive-1',{'closed'},10);result['positive']=row
 cli('dispatch','--qid','P8-timeout-1','--worker',w,'--verifier',v,'--task','@'+str(P/'live-hung-task-1.txt'),'--verify-task','No verifier should run for this timed-out fixture. Do not act.','--duration','90s','--verify-window','60s')
 row=wait_step('P8-timeout-1',{'timed-out'},180);result['timeout']=row;time.sleep(20)
 result['final_status']=status();result['state']='OBSERVATIONS_COMPLETE_REQUIRES_INDEPENDENT_REVIEW'
except Exception as exc:result['error']=str(exc)
finally:
 try:stop()
 except Exception as exc:result['stop_error']=str(exc)
 result['ended_at']=now().isoformat();(E/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 # All remaining timers are confined to this signed unique project prefix.
 r=call(['systemctl','--user','list-units','--all','--plain','--no-legend','agent-loop-p8-live1-*'],check=False)
 for line in r.stdout.splitlines():
  unit=line.split()[0]
  if unit.startswith('agent-loop-p8-live1-') and unit.endswith(('.timer','.service')):call(['systemctl','--user','stop',unit],check=False)
 for x in ('loop.db','loop.db-wal','loop.db-shm'):
  if (R/x).exists():shutil.copy2(R/x,E/x)
 for d in ('claims','artifacts'):
  if (R/d).exists():shutil.copytree(R/d,E/d,dirs_exist_ok=True)
 for x in json.loads((P/'execution-binding-1.json').read_text())['roles'].values():
  f=Path(cfg['stream_dir'])/(x['session_id']+'.jsonl')
  if f.exists():shutil.copy2(f,E/f.name)
 call([sys.executable,str(P/'cleanup-preparation-1.py')],check=False,timeout=240)
 call(['systemctl','--user','stop','campaign4-p8-prep1-cleanup.timer'],check=False)
print(json.dumps(result));sys.exit(0 if result['state'].startswith('OBSERVATIONS_COMPLETE') else 3)
