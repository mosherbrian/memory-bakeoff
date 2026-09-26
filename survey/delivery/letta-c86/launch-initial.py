import os,subprocess,sys,json
from pathlib import Path
ROOT=Path('/tmp/tern-letta-c86')
arm=sys.argv[1]
assert arm in ('L','N')
network='--network' in sys.argv
args=[a for a in sys.argv[2:] if a!='--network']
pkg='@letta-ai/letta-code/letta.js' if arm=='L' else '@earendil-works/pi-coding-agent/dist/cli.js'
cmd=['bwrap','--unshare-all','--die-with-parent']
if network:cmd+=['--share-net']
cmd+=['--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--ro-bind','/etc','/etc','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home','--bind',str(ROOT/'arms'/arm/'home'),'/home/bmosher','--dir','/var','--symlink','/home','/var/home','--ro-bind',str(ROOT/'install'),'/opt/harness','--bind',str(ROOT/'arms'/arm/'project'),'/work','--chdir','/work','/usr/bin/node','/opt/harness/node_modules/'+pkg]+args
if network:
    pos=cmd.index('--chdir')
    cmd[pos:pos]=['--ro-bind',str(ROOT/'fetch-guard.mjs'),'/fetch-guard.mjs','--bind',str(ROOT/'arms'/arm/'control'),'/trial-control']
    if Path('/run/NetworkManager').exists():cmd[pos:pos]=['--ro-bind','/run/NetworkManager','/run/NetworkManager']
    if Path('/run/systemd/resolve').exists():cmd[pos:pos]=['--ro-bind','/run/systemd/resolve','/run/systemd/resolve']
env={k:v for k,v in os.environ.items() if k in ('HOME','USER','LOGNAME','LANG','TZ')}
env.update(PATH='/usr/bin:/bin',PI_OFFLINE='1',DO_NOT_TRACK='1',LETTA_DISABLE_TELEMETRY='1',LETTA_DISABLE_MODS='1')
for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','http_proxy','https_proxy','all_proxy','no_proxy'):
    if key in os.environ:env[key]=os.environ[key]
if network:env['NODE_OPTIONS']='--import=/fetch-guard.mjs'
os.execve('/usr/bin/bwrap',cmd,env)
