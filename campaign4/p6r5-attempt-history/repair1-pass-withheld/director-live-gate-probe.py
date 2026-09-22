"""No live effects: probe evidence authenticity and acceptance timing."""
import json,subprocess,sys,tempfile
from pathlib import Path
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p/'src'))
from harness import check_latency
root=Path(tempfile.mkdtemp(prefix='p6r5-director-'))
r=subprocess.run([sys.executable,str(p/'src/prepare_evidence.py'),'--producer-root',str(root),'--session','invented-session','--stream-key','invented-main','--worker-stream-key','invented-worker','--verifier-stream-key','invented-verifier'],capture_output=True,text=True)
row={'outcome':'terminal-rest','source_at':None,'source_time_known':False,'dispatch_at':'2026-09-22T03:00:00Z','detected_at':'2026-09-22T03:00:01Z','committed_at':'2026-09-22T03:00:02Z'}
f=root/'latency.jsonl'; f.write_text(json.dumps(row)+'\n')
print(json.dumps({'empty_root_preparation':{'rc':r.returncode,'evidence':json.loads(r.stdout)},'unknown_source_latency':check_latency(str(f))},sort_keys=True))
