"""Director probe: injected transport only; count all sends on exact CLI."""
import json, sys
from pathlib import Path
p=Path(__file__).resolve().parent
sys.path[:0]=[str(p/'tests'),str(p/'src')]
import test_cli_acceptance as t
tmp=t.mktree(); env=t.write_shims(tmp); plan,ph=t.write_plan(tmp)
t.run_cli(['--plan',plan,'--manifest',tmp+'/manifest.json','--session','sess-ev','--stream-key','sk-ev','setup'],env)
m=json.load(open(tmp+'/manifest.json'))
t.stage_worker(tmp,m); t.append_end(tmp,m); t.append_vend(tmp,m)
t.stage_claim(tmp,m); t.stage_claim(tmp,m,execution=m['verify_execution_id'],step='verify-run')
rc,out=t.run_cli(t.live_args(tmp,plan,ph,['run-fixture']),env)
trace=Path(tmp+'/trace.log').read_text().splitlines()
sends=[x for x in trace if x.startswith('CALL wake p6-fixture-verifier')]
print(json.dumps({'rc':rc,'decision':out.get('decision'),'verifier_send_count':len(sends),'verifier_sends':sends,'expected':1},sort_keys=True))
