# NET1-C — Office gateway health + model check (run from home laptop context)

Context: home laptop `strix-halo` (Fedora). Office gateway: `cds-ai-a5410.cds.dmrc.lcl:8300`, assistant `Qwen`, model `qwen3.8-flash-next`. I did not probe the gateway from here; run the checks below.

## 1. Gateway healthy?

```bash
curl -sS -m 10 http://cds-ai-a5410.cds.dmrc.lcl:8300/health -o /tmp/gw-health.json -w 'HTTP %{http_code}\n'
cat /tmp/gw-health.json
```

Healthy = HTTP 200 with a status field like `"ok"` / `"healthy"` (exact key depends on gateway; any non-200, timeout, or DNS/refused error = not healthy).

If this host serves OpenAI-compatible API instead, also try:

```bash
curl -sS -m 10 http://cds-ai-a5410.cds.dmrc.lcl:8300/v1/models | head -c 2000; echo
```

## 2. Is `qwen3.8-flash-next` loaded?

```bash
curl -sS -m 15 http://cds-ai-a5410.cds.dmrc.lcl:8300/v1/models | python3 -c "import json,sys; d=json.load(sys.stdin); ms=[m.get('id') for m in d.get('data',[])]; print('\n'.join(ms)); print('MATCH' if 'qwen3.8-flash-next' in ms else 'NOT-LOADED')"
```

Alternatives if the gateway has its own endpoint (try in order, use whichever exists):
- `GET /models`, `GET /loaded-models`, or the health JSON's model list.
- Check the Qwen assistant config on the office side for its configured model name.

## 3. What to do if not

- **Gateway unreachable (DNS / timeout / refused):** you are likely off VPN / office network. Connect to the office network or VPN, confirm the hostname resolves (`getent hosts cds-ai-a5410.cds.dmrc.lcl`), retry. If still down, check on the office host whether the gateway service is running and port 8300 is listening, then restart it.
- **Gateway up but non-200 health:** read the body in `/tmp/gw-health.json`, check gateway logs on the office host, restart the service if needed.
- **Model not loaded:** load/pull `qwen3.8-flash-next` on the office host per that gateway's procedure (model pull or config update + restart), then re-run step 2 until `MATCH`.
- **Wrong name:** if the loaded ID differs slightly (e.g. version suffix), either load the exact `qwen3.8-flash-next` ID or update the Qwen assistant config to the loaded ID — but keep the naming explicit so later runs are comparable.

Report back: the HTTP code from step 1, the `MATCH`/`NOT-LOADED` line from step 2, and any action taken.
