import json,subprocess,time,sys,hashlib,signal,os
from pathlib import Path
from score import score
ROOT=Path('/tmp/tern-letta-c86');E=ROOT/'evidence'
prompts=json.loads((ROOT/'prompts.json').read_text())
agent='agent-local-3bb72e5e-c262-4430-9c61-1c40807445e7'
limits={1:4,2:4,3:5,4:3,5:6,6:6,7:5}
records=[]
def invoke(arm,session,prompt,suffix=''):
 stem=f'{arm}-s{session}{suffix}'
 if arm=='L':
  args=['--backend','local','--agent',agent,'--new','--model','gpt-5.6-sol-low','--reflection-trigger','step-count','--reflection-step-count','5','--max-turns',str(limits[session]),'--permission-mode','bypassPermissions','--output-format','json','-p',prompt]
 else:args=['--provider','openai-codex','--model','gpt-5.6-sol','--thinking','low','--no-extensions','--mode','json','-p',prompt]
 started=time.time()
 with (E/f'{stem}.out').open('w') as out,(E/f'{stem}.err').open('w') as err:
  p=subprocess.Popen([sys.executable,str(ROOT/'launch.py'),arm,'--network',*args],stdout=out,stderr=err,start_new_session=True)
  try:rc=p.wait(timeout=240)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10);rc=124
 result={'arm':arm,'session':session,'retry':bool(suffix),'ready_at':started,'ended_at':time.time(),'returncode':rc}
 usage=json.loads((ROOT/'arms'/arm/'control/usage.json').read_text());result['cumulative_usage']=usage
 text=(E/f'{stem}.out').read_text()
 errors=[]
 if arm=='L':
  try:
   response=json.loads(text);result['harness_usage']=response.get('usage');errors += [response.get('error') or response.get('result')] if response.get('is_error') else []
  except ValueError:errors.append('No parseable Letta result')
 else:
  for line in text.splitlines():
   try:d=json.loads(line)
   except ValueError:continue
   if d.get('type')=='message_end' and d.get('message',{}).get('role')=='assistant' and d['message'].get('stopReason')=='error':errors.append(d['message'].get('errorMessage','provider error'))
 result['errors']=errors
 if session>=5:result['scores']=score(ROOT/'arms'/arm/'project',session)
 records.append(result);(ROOT/'run-records.json').write_text(json.dumps(records,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k not in ('cumulative_usage','harness_usage')}),flush=True)
 if rc or errors or usage['calls']>=30 or usage['input_tokens']>250000 or usage['output_tokens']>20000:
  (ROOT/'terminal.json').write_text(json.dumps({'status':'inconclusive','reason':'Harness/resource boundary','last_record':result},indent=2));raise SystemExit(2)
 return result
reminders={'atlas_schema':'Atlas format is exactly question_id, owner, artifact.','beacon_schema':'Beacon format is exactly task_id, owner, evidence.','atlas_route':'Atlas current recipient is cairn, replacing kiln.','beacon_folder':'Beacon completion files belong in accepted/, not drafts/.','artifact_procedure':'Build the artifact first with tools.py build, then tools.py digest, then write artifact/sha256/status ready JSON.','evidence_procedure':'Use tools.py verify on the exact evidence before tools.py close TASK EVIDENCE OUTPUT.'}
manifest=json.loads((ROOT/'pre-run-manifest.json').read_text());manifest.update(scored_tasks_started=True,start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),setup_completed=True,transport='SSE forced for uniform per-request accounting',isolation='bubblewrap separate homes and projects; other arm and scoring files not mounted',setup_successful_requests_per_arm=2,source_commit='2394082e236318cad95de1dd783ab22965dde597')
(ROOT/'frozen-manifest.json').write_text(json.dumps(manifest,indent=2))
for session in range(1,8):
 for arm in (['L','N'] if session%2 else ['N','L']):
  r=invoke(arm,session,prompts[str(session)])
  if session in (5,6):
   failures=[k for k,v in r['scores'].items() if not v]
   if failures:invoke(arm,session,'One correction per failed task: '+' '.join(reminders[k] for k in failures)+' Repair only those failed outputs for session '+str(session)+'.','-retry')
summary={}
for arm in ('L','N'):
 later=[r for r in records if r['arm']==arm and r['session'] in (5,6) and not r['retry']]
 controls=[r for r in records if r['arm']==arm and r['session']==7][0]
 correct=sum(sum(r['scores'].values()) for r in later)
 summary[arm]={'correct_first_of12':correct,'reminders':12-correct,'wrong_controls_of4':4-sum(controls['scores'].values()),'usage':json.loads((ROOT/'arms'/arm/'control/usage.json').read_text())}
l,n=summary['L'],summary['N'];passed=l['correct_first_of12']>=10 and l['correct_first_of12']-n['correct_first_of12']>=2 and n['reminders']-l['reminders']>=2 and l['wrong_controls_of4']==0
(ROOT/'terminal.json').write_text(json.dumps({'status':'pass' if passed else 'fail_to_justify_switch','arms':summary,'operator_memory_repairs':0},indent=2))
print('TERMINAL '+('PASS' if passed else 'FAIL TO JUSTIFY SWITCH'),flush=True)
