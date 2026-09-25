I can't reach the office network from your home laptop, so run these on your work machine (or ask Qwen):
```bash
curl -s http://cds-ai-a5410.cds.dmrc.lcl:8300/health
curl -s http://cds-ai-a5410.cds.dmrc.lcl:8300/v1/models | python -c "import json,sys;print([m['id'] for m in json.load(sys.stdin)['data']])"
```
If /health is not ok, restart with `systemctl --user restart igw-router` on that box.
