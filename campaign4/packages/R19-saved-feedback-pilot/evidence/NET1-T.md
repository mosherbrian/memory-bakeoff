# NET1-T — Office gateway health + model check (from home laptop strix-halo)

I did **not** check the office gateway from here. From your home laptop on your home network, the office hosts (`cds-ai-a5410.cds.dmrc.lcl` and the other `cds-ai-a54xx` machines) are not reachable. So anything below is for you or Qwen to run **office-side**, not something I ran.

## What to run office-side (hand to Qwen)

Qwen, on an office machine that can resolve `cds-ai-a5410.cds.dmrc.lcl`, run:

```
python -c "import urllib.request, json; print(urllib.request.urlopen('http://cds-ai-a5410.cds.dmrc.lcl:8300/health', timeout=10).read().decode())"
```

Then check the model:

```
python -c "import urllib.request, json; print(urllib.request.urlopen('http://cds-ai-a5410.cds.dmrc.lcl:8300/models', timeout=10).read().decode())"
```

Look for `qwen3.8-flash-next` (exact name) in the models output. If your gateway uses different paths (e.g. `/v1/models` or `/healthz`), substitute those and tell Brian which path worked.

Note: services office-side should bind to `0.0.0.0` (all interfaces) so other office machines can reach them; when opening in a browser use the resolvable hostname `cds-ai-a5410.cds.dmrc.lcl` with the port, never a loopback address.

## What to do if not healthy / model not loaded

1. **Gateway not responding:** SSH to `cds-ai-a5410.cds.dmrc.lcl` office-side, check the gateway process / service status, restart it per its normal procedure, then re-run the health check above.
2. **Gateway healthy but model missing:** load `qwen3.8-flash-next` through the gateway's normal model-load step (whatever your gateway uses — config entry or load endpoint), then re-run the models check and confirm the exact name appears.
3. **Still failing:** paste back the exact command output (health + models) plus the gateway log tail so the failure is diagnosable. Do not report it as healthy on the basis of a retry without output.

## Bottom line for Brian

No office check was performed from `strix-halo` — it can't be, across the home/office network split. Hand the two commands above to Qwen office-side; healthy means: health endpoint returns OK, and the models list contains `qwen3.8-flash-next`.
